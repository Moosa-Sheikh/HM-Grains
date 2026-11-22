// Display a form result after the PHP endpoint redirects back to Contact.
if (location.pathname.replace(/\/+$/, '/') === '/contact/') {
  const params = new URLSearchParams(location.search);
  const status = params.get('sent') === '1'
    ? 'Thank you! Your message has been sent.'
    : params.has('error') ? 'Sorry, your message could not be sent. Please check your details or email contact@hmgrains.com.' : '';
  if (status) {
    const form = document.querySelector('#wpforms-form-16');
    if (form) {
      const notice = document.createElement('p');
      notice.className = 'contact-notice';
      notice.setAttribute('role', 'status');
      notice.textContent = status;
      form.before(notice);
      notice.scrollIntoView({ block: 'center' });
    }
  }
}
