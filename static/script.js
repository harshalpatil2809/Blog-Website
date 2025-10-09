document.addEventListener("DOMContentLoaded", function () {
  const menu = document.getElementById("mobile-menu");
  const openBtn = document.getElementById("menu-btn");
  const closeBtn = document.getElementById("close-menu");

  openBtn.addEventListener("click", () => {
    menu.classList.remove("translate-x-full");
    menu.classList.add("translate-x-0");
  });

  closeBtn.addEventListener("click", () => {
    menu.classList.remove("translate-x-0");
    menu.classList.add("translate-x-full");
  });
});
