window.addEventListener('scroll', function () {
    var header = document.getElementById('header');
    if (window.scrollY > 50) {  // Change 50 to the scroll position where you want the change to happen
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });