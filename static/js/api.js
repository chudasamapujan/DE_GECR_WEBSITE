// Minimal API shim used by frontend pages
window.GECUtils = window.GECUtils || {};
GECUtils.API = {
    post: function(path, body) {
        return fetch(path, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) })
            .then(r => r.json().then(j => ({ ok: r.ok, status: r.status, body: j })))
    }
};
