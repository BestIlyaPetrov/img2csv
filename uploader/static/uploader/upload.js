document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('upload-form');
  const processing = document.getElementById('processing');

  if (!form) return;

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const formData = new FormData(form);
    processing.style.display = 'block';
    fetch('/process-image/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken
      },
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        processing.style.display = 'none';
        if (data.csv_data) {
          const blob = new Blob([data.csv_data], { type: 'text/csv' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'table.csv';
          a.click();
          window.URL.revokeObjectURL(url);
        } else if (data.error) {
          alert(data.error);
        }
      })
      .catch(() => {
        processing.style.display = 'none';
        alert('An error occurred while processing the image.');
      });
  });
});
