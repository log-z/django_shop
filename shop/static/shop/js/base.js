window.addLoadEvent = call => {
    let old_onload = window.onload;

    if (typeof window.onload !== 'function') {
        window.onload = call;
    } else {
        window.onload = function() {
            old_onload();
            call();
        }
    }
};

function form_dataset(form) {
    let dataset = [];
    let inputs = form.querySelectorAll('input');

    dataset.push('option=' + form.getAttribute('option'));
    for (let i = 0; i < inputs.length; i++) {
        dataset.push(inputs[i].name + '=' + inputs[i].value)
    }

    return dataset.join('&');
}

function default_restful_handel(form, xlr) {
    if (xlr.readyState !== 4) return;

    let tips = form.querySelector('.tips');
    let data = JSON.parse(xlr.responseText);
    if (xlr.status === 200) {
        tips.innerText = data.result;
    } else {
        tips.innerText = data.error;
        tips.classList.add('error');
    }
}

function form_restful_init() {
    let forms = document.querySelectorAll('form');
    for (let i = 0; i < forms.length; i++) {
        if (forms[i].getAttribute('submit-type') !== 'restful') continue;

        forms[i].onsubmit = ev => {
            ev.preventDefault();
            let form = ev.target;
            let xlr = new XMLHttpRequest();

            xlr.open(form.method, form.action, true);
            xlr.setRequestHeader('Accept', 'application/json');
            xlr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xlr.onreadystatechange = () => default_restful_handel(form, xlr);
            xlr.send(form_dataset(form));
        }
    }
}

window.addLoadEvent(() => {
    form_restful_init();
});
