let running = true

setTimeout(() => {
    a(10)
}, $timeout$)

function a(delay) {
    setTimeout(() => {
        check()
        b(delay)
    }, delay)
}

function b(delay) {
    setTimeout(() => {
        check()
        a(delay)
    }, delay)
}

function check() {
    let elements = document.getElementsByClassName('MatchModeQuestionGridTile-text')
    if (elements.length === 12 && running) {
        let words = ''

        for (const element of elements) {
            const word = element.children[0].innerHTML
            words += word + ';;'
        }

        navigator.clipboard.writeText(words)
        console.log(words)
        running = false
    }
}