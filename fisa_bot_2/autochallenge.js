// ==UserScript==
// @name       PyTron auto challenger
// @namespace  http://pytron.onapsis.com
// @version    0.1
// @description  auto challenge new bots on the pytron challenge
// @match      https://pytron.onapsis.com/scoreboard
// @copyright  2013+, Juan Pedro Fisanotti
// ==/UserScript==

pending = $('a.btn:contains("Pending")');
challenge = $('a.btn:contains("Challenge")');

setTimeout(function(){
    window.location.reload(1);
}, 30000);

function silentPostBot(bot_button) {
    var data = parseInt($(bot_button).attr('onclick').replace('postBot(', '').replace(", '/challenge')", ""));

    console.log('Bot: ' + data.toString());

    $.ajax({
        url: '/challenge',
        type: "POST",
        data: JSON.stringify({ msg: data}),
        dataType: "json",
        async: false,
        contentType: "application/json"
    }).fail(function(xhr, textStatus, errorThrown) {
        alert(xhr.responseText);
    }).done(function() {
        location.reload();
    })
}

if (pending.length == 0) {
    if (challenge.length > 0) {
        if (parseInt($('tr:contains("fisadev") td')[2].textContent) > 650) {
            console.log('Challenge!');
            silentPostBot(challenge[0]);
        }
    } else {
        console.log('Nothing to do');
    }
} else {
    console.log('Pendig challenge...');
}
