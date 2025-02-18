const butimgL = document.querySelector('.spbutL')
const butimgR = document.querySelector('.spbutR')
const backclass = document.querySelector('.bg-animation')
let i = 0
let j = 0

function checkVariable() {
    if (j === i) {
      i += 1
      changeimg ()
    } else {
      j = i
    }
}

// Запускаем функцию checkVariable каждые 30 секунд
const intervalId = setInterval(checkVariable, 30000);

butimgR.addEventListener('click', () => {
    clearInterval(intervalId)
    i += 1
    changeimg ()
})

butimgL.addEventListener('click', () => {
    clearInterval(intervalId)
    i -= 1
    changeimg ()
})

function changeimg () {
if ( Math.abs(i % 3) == 1 ) {
    backclass.classList.remove('partback')
    backclass.classList.remove('saunaback')
    backclass.classList.add('hamamback');
} else if ( Math.abs(i % 3) == 2 ) {
    backclass.classList.remove('hamamback')
    backclass.classList.remove('partback')
    backclass.classList.add('saunaback');
} else if ( Math.abs(i % 3) == 0 ) { 
    backclass.classList.remove('saunaback')
    backclass.classList.remove('hamamback')
    backclass.classList.add('partback');
}
}