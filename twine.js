const STARTUP_TIMEOUT = 2000;
const RECONNECT_TIMEOUT = 1000;
const PY_SERVER = 'ws://localhost:5000';

let ws;
let last_message;

(function init_ws() {
    console.log(`connecting to python at ${PY_SERVER}`);
    ws = new Promise(r => {
        const w = new WebSocket(PY_SERVER);

        // delay doing anything for a moment once we connect
        // python seems to be happier this way or something...
        w.onopen = () => setTimeout(() => r(w), STARTUP_TIMEOUT);

        w.onclose = () => {
            console.log(`disconnected.\ntrying to reconnect in ${RECONNECT_TIMEOUT}ms...`);
            setTimeout(() => {
                init_ws();
                ws.then(w => w.send(last_message));
            }, RECONNECT_TIMEOUT);
        };
    });

    ws.then(w => w.onmessage = e => {
        const data = JSON.parse(e.data);
        if (data.restart === 'please') {
            console.log('restart');
            return Engine.restart();
        }
        console.log('play', data.passage);
        Engine.play(data.passage);
    });
})();


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

    console.log('sending', processed.innerText.trim());
    const message = JSON.stringify(nice);
    last_message = message;
    ws.then(w => {
        w.send(message);
    });
});
