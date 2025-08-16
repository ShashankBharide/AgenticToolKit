(function () {
    function freeze(node) {
        Object.freeze(node);
        for (const child of node.children) {
            freeze(child);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        freeze(document.documentElement);
        const observer = new MutationObserver(() => {
            observer.disconnect();
            freeze(document.documentElement);
            observer.observe(document, { subtree: true, childList: true, attributes: true });
        });
        observer.observe(document, { subtree: true, childList: true, attributes: true });
    });
})();
