function scrollToAuth() {
    const target = window.parent.document.getElementById('auth-section');
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
scrollToAuth();
