window.onscroll = () => {
    const header = document.querySelector('.nav');
    const body = document.querySelector('.main');
    const Y = window.scrollY
    

    if (Y > 82) {
        header.classList.add("nav_fixed");
        body.classList.add("with_nav");
    } else if (Y < 81) {
        header.classList.remove("nav_fixed");
        body.classList.remove("with_nav");
    }
}