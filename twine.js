const ws = new Promise(r => {
    const w = new WebSocket('ws://localhost:5000');
    w.onopen = () => {
        setTimeout(() => r(w), 1000);
    };
});

ws.then(w => w.onmessage = e => {
    const data = JSON.parse(e.data);
    console.log('play', data.passage);
    Engine.play(data.passage);
});

$(document).on(':passagerender', ev => {
    const content = ev.content;
    const processed = content.cloneNode(true);
    const linkEls = processed.querySelectorAll('a');
    const links = [];
    for (let i = 0; i < linkEls.length; i++) {
        const link = linkEls[i];
        links.push({
            passage: link.dataset.passage,
            name: link.textContent,
        });
        link.parentNode.removeChild(link);
    }
    const nice = {
        text: processed.innerText.trim(),
        links: links,
    };

    ws.then(w => {
        w.send(JSON.stringify(nice))
    });
    //console.log('nice', nice);
});
