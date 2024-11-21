const butimgL = document.querySelector('.spbutL')
const butimgR = document.querySelector('.spbutR')
const backclass = document.querySelector('.bg-animation')
let i = 0

setInterval(() => {
    i += 1;
    changeimg ()
  }, 15000);

butimgR.addEventListener('click', () => {
    i += 1
    changeimg ()
})

butimgL.addEventListener('click', () => {
    i -= 1
    changeimg ()
})

function changeimg () {
if ( Math.abs(i % 3) == 1 ) {
    backclass.classList.remove('partback');
    backclass.classList.toggle('hamamback');
} else if ( Math.abs(i % 3) == 2 ) {
    backclass.classList.toggle('hamamback')
    backclass.classList.toggle('saunaback');
} else if ( Math.abs(i % 3) == 0 ) { 
    backclass.classList.toggle('saunaback')
    backclass.classList.toggle('partback');
}
}