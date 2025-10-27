const one = document.getElementById('first')
const two = document.getElementById('second')
const three = document.getElementById('third')
const four = document.getElementById('fourth')
const five = document.getElementById('fifth')

const form = document.querySelector('.rate-form')
const confirmBox = document.getElementById('confirm-box')

const csrf = document.getElementsByName('csrfmiddlewaretoken')

const handleStarSelect = (size) => {
    const children = form.children
    for (let i = 0; i < children.length; i++) {
        if (i <= size) {
            children[i].classList.add('checked')
        }
        else {
            children[i].classList.remove('checked')
        }
    }
}

//longer version to be optimized
const handleSelect = (selection) => {
    switch (selection) {
        case 'first': {
            // one.classList.add('checked')
            // two.classList.remove('checked')
            // three.classList.remove('checked')
            // four.classList.remove('checked')
            // five.classList.remove('checked')
            handleStarSelect(1)
            return
        }
        case 'second': {
            // one.classList.add('checked')
            // two.classList.add('checked')
            // three.classList.remove('checked')
            // four.classList.remove('checked')
            // five.classList.remove('checked')
            handleStarSelect(2)
            return
        }
        case 'third': {
            // one.classList.add('checked')
            // two.classList.add('checked')
            // three.classList.add('checked')
            // four.classList.remove('checked')
            // five.classList.remove('checked')
            handleStarSelect(3)
            return
        }
        case 'fourth': {
            // one.classList.add('checked')
            // two.classList.add('checked')
            // three.classList.add('checked')
            // four.classList.add('checked')
            // five.classList.remove('checked')
            handleStarSelect(4)
            return
        }
        case 'fifth': {
            // one.classList.add('checked')
            // two.classList.add('checked')
            // three.classList.add('checked')
            // four.classList.add('checked')
            // five.classList.add('checked')
            handleStarSelect(5)
            return
        }
    }
}

if (one) {
    const arr = [one, two, three, four, five]
    arr.forEach(item => item.addEventListener('mouseover', (event) => { handleSelect(event.target.id) }))
    arr.forEach(item => item.addEventListener('click', (event) => {
        const val = event.target.id

        form.addEventListener('submit', e => {
            e.preventDefault()
            const id = e.target.id
        })
    }))

}
