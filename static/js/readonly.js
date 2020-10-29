$(document).ready(function() {
    showHtml();
    hideId();
    hideActions();
});

/**
 * HTMLの内容を表示する
 */
function showHtml() {
    let labelNode = document.evaluate(
        "//label[contains(., 'メール本文')]", document, null, XPathResult.ANY_TYPE, null
    ).iterateNext();
    if (labelNode) {
        let htmlNode = labelNode.nextSibling.nextSibling;
        let html = htmlNode.innerHTML;
        let div = document.createElement("div");
        div.setAttribute("contenteditable", "true");
        div.setAttribute("class", "readonly");
        div.innerHTML = html;
        htmlNode.replaceWith(div);
    }
}

function hideId() {
    let idNode = document.evaluate(
        "//label[contains(., 'ID:')]", document, null, XPathResult.ANY_TYPE, null
    ).iterateNext();
    idNode.parentElement.parentElement.remove();
}

function hideActions() {
    document.querySelector('div.submit-row').remove();
}
