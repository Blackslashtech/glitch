/*!
 * jQuery CLI
 * Simulating a command line interface with jQuery
 *
 * @version : 1.0.0
 * @author : Paulo Nunes (http://syndicatefx.com)
 * @demo : https://codepen.io/syndicatefx/pen/jPxXpz
 * @license: MIT
 */

/*!* 
 * jQuery Text Typer plugin
 * https://github.com/gr8pathik/jquery-texttyper
*/

var star_id = null;

var types = [
    'Unknown',
    'Terrestrial',
    'Protoplanet',
    'GasGiant'
]

function get_last_stars(n) {
    var res = $.ajax({
        url: '/api/stars/',
        type: 'GET',
        async: false,
        dataType: 'json'
    });

    if (res.status == 500) {
        return {'error': 'internal server error'};
    }
    
    return res.responseJSON.splice(0, n);
}

function get_star(star_id) {
    var res = $.ajax({
        url: `/api/stars/${star_id}`,
        type: 'GET',
        async: false,
        dataType: 'json'
    });

    if (res.status == 500) {
        return {'error': 'internal server error'};
    }

    return res.responseJSON;
}

function get_planet(planet_id) {
    var res = $.ajax({
        url: `/api/planets/${planet_id}`,
        type: 'GET',
        async: false,
        dataType: 'json'
    });

    if (res.status == 500) {
        return {'error': 'internal server error'};
    }

    res = res.responseJSON;
    res.type = types[res.type];

    return res;
}

function add_star(star) {
    var res = $.ajax({
        url: `/api/stars/`,
        type: 'POST',
        async: false,
        contentType: "application/json",
        data: JSON.stringify(star)
    });

    if (res.status == 500) {
        return {'error': 'internal server error'};
    }

    if (res.status == 201) {
        star_id = res.responseJSON.id;
    }

    return res.responseJSON;
}

function add_planet(planet) {
    var res = $.ajax({
        url: `/api/planets/`,
        type: 'POST',
        async: false,
        contentType: "application/json",
        data: JSON.stringify(planet)
    });

    if (res.status == 500) {
        return {'error': 'internal server error'};
    }

    return res.responseJSON;
}

$(document).ready(function() {
    $('.command').hide();
    $('input[type="text"]').focus();
    $('#clear').addClass('open');
    $('.command').fadeIn();
    $('input[type="text"]').focus();
    $('input[type="text"]').val('');

    var sectionArray = [];

    $('section').each( function(i,e) {
        sectionArray.push($(e).attr('id'));
    });

    $('input[type="text"]').keyup(function(e){

        if(e.which == 13) {

            $('.command').hide();
            var destination = $('input[type="text"]').val();

            var parts = destination.split(' ');
            var content = document.getElementById('content');

            while (content.firstChild) {
                content.firstChild.remove();
            }

            document.getElementById('kek').innerText = destination;

            switch (parts[0]) {
                case 'last':
                    destination = 'content';
                    
                    var n = Math.max(0, Math.min(parts[1] || 10, 100));
                    
                    var p = document.createElement('p');
                    p.innerText = `getting last ${n} stars...`;
                    content.appendChild(p);

                    var stars = get_last_stars(n);
                    var ul = document.createElement('ul');

                    for (var star of stars) {
                        var li = document.createElement('li');
                        var pre = document.createElement('pre');
                        pre.innerText = JSON.stringify(star, null, 2);
                        li.appendChild(pre);
                        ul.appendChild(li);
                    }

                    content.appendChild(ul);
                    break;
                
                case 'get':
                    destination = 'content';

                    var obj = parts[1];

                    if (!obj) {
                        var p = document.createElement('p');
                        p.innerText = 'Invalid command!'
                        var pre = document.createElement('pre');
                        pre.innerText = "usage: 'get <star | planet> <id>'";
                        content.appendChild(p);
                        content.appendChild(pre);
                        break;
                    }

                    if (obj == 'star') {
                        var id = parts[2];

                        if (!id) {
                            var p = document.createElement('p');
                            p.innerText = 'Invalid command!'
                            var pre = document.createElement('pre');
                            pre.innerText = "usage: 'get star <id>'";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }

                        var p = document.createElement('p');
                        p.innerText = 'getting star...';
                        content.appendChild(p);
                        
                        var star = get_star(id);
                        var pre = document.createElement('pre');
                        pre.innerText = JSON.stringify(star, null, 2);
                        content.appendChild(pre);
                    } else if (obj == 'planet') {
                        var id = parts[2];
    
                        if (!id) {
                            var p = document.createElement('p');
                            p.innerText = 'Invalid command!'
                            var pre = document.createElement('pre');
                            pre.innerText = "usage: 'get planet <id>'";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }
    
                        var p = document.createElement('p');
                        p.innerText = 'getting planet...';
                        content.appendChild(p);
                        
                        var planet = get_planet(id);
                        var pre = document.createElement('pre');
                        pre.innerText = JSON.stringify(planet, null, 2);
                        content.appendChild(pre);
                    } else {
                        var p = document.createElement('p');
                        p.innerText = 'Invalid command!'
                        var pre = document.createElement('pre');
                        pre.innerText = "usage: 'get <star | planet> <id>'";
                        content.appendChild(p);
                        content.appendChild(pre);
                    }

                    break;

                case 'add':
                    destination = 'content';

                    var obj = parts[1];

                    if (!obj) {
                        var p = document.createElement('p');
                        p.innerText = 'Invalid command!'
                        var pre = document.createElement('pre');
                        pre.innerText = "usage: 'add <star | planet> [params...]'";
                        content.appendChild(p);
                        content.appendChild(pre);
                        break;
                    }

                    if (obj == 'star') {
                        var name = parts[2];
                        var location = parts[3];
    
                        if (!name || !location) {
                            var p = document.createElement('p');
                            p.innerText = 'Invalid command!'
                            var pre = document.createElement('pre');
                            pre.innerText = "usage: 'add star <name> <location>'";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }
    
                        var star = {
                            'name': name,
                            'location': location
                        }
    
                        var p = document.createElement('p');
                        p.innerText = 'creating star...';
                        content.appendChild(p);
                        
                        var star = add_star(star);
                        var pre = document.createElement('pre');
                        pre.innerText = JSON.stringify(star, null, 2);
                        content.appendChild(pre);
                    } else if (obj == 'planet') {
                        var name = parts[2];
                        var location = parts[3];
                        var type = parts[4] || 'Unknown';
                        var public = parts[5] || 'true';
    
                        if (!name || !location) {
                            var p = document.createElement('p');
                            p.innerText = 'Invalid command!'
                            var pre = document.createElement('pre');
                            pre.innerText = "usage: 'add planet <name> <location> [type=Unknown] [public=true]'";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }
    
                        if (types.indexOf(type) == -1) {
                            var p = document.createElement('p');
                            p.innerText = 'Invalid type!'
                            var pre = document.createElement('pre');
                            pre.innerText = "use 'types' to see available types";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }
    
                        if (public != 'true' && public != 'false') {
                            var p = document.createElement('p');
                            p.innerText = 'Invalid parameter!'
                            var pre = document.createElement('pre');
                            pre.innerText = "public must be 'true' or 'false'";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }
    
                        if (!star_id) {
                            var p = document.createElement('p');
                            p.innerText = "Can't create a planet!"
                            var pre = document.createElement('pre');
                            pre.innerText = "please, create a star first";
                            content.appendChild(p);
                            content.appendChild(pre);
                            break;
                        }
    
                        var planet = {
                            'starId': star_id,
                            'name': name,
                            'location': location,
                            'type': types.indexOf(type),
                            'isHidden': public == 'false'
                        }
    
                        var p = document.createElement('p');
                        p.innerText = 'creating planet...';
                        content.appendChild(p);
                        
                        var planet = add_planet(planet);
                        var pre = document.createElement('pre');
                        pre.innerText = JSON.stringify(planet, null, 2);
                        content.appendChild(pre);
                    } else {
                        var p = document.createElement('p');
                        p.innerText = 'Invalid command!'
                        var pre = document.createElement('pre');
                        pre.innerText = "usage: 'add <star | planet> [params...]'";
                        content.appendChild(p);
                        content.appendChild(pre);
                        break;
                    }

                    break;

                case 'content':
                    destination = 'error';
                    
                    break;
            }

            $('section[id="' + destination + '"]').addClass('open').siblings().removeClass('open');
            
            if($.inArray(destination, sectionArray) == -1){
                $('#error').addClass('open');
                $('#error').siblings().removeClass('open');
            }

            $('.command').fadeIn();
            $('input[type="text"]').focus();
            $('input[type="text"]').val('');
        
            $('html,body').animate({scrollTop: document.body.scrollHeight}, "fast");

        }

    });

});
