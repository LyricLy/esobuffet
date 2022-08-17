function doUnit(s, ms, amount, unit) {
    let u = Math.floor(ms / amount);
    if (u) {
        s.push(`${u} ${unit}${u > 1 ? "s" : ""}`);
    }
    return ms % amount;
}

for (const elem of document.getElementsByClassName("datetime")) {
    let date = new Date(elem.innerText.trim());
    if (date < new Date()) {
        elem.innerHTML = date.toLocaleString();
        continue;
    }
    let f = () => {
        let ms = date - new Date();
        if (ms < 0) {
            elem.innerHTML = date.toLocaleString();
            return;
        }
        let s = [];
        ms = doUnit(s, ms, 1000*60*60*24, "day");
        ms = doUnit(s, ms, 1000*60*60, "hour");
        ms = doUnit(s, ms, 1000*60, "minute");
        ms = doUnit(s, ms, 1000, "second");
        elem.innerHTML = `${date.toLocaleString()} (${s.join(", ")})`;
    };
    f();
    setInterval(f, 1000);
}
