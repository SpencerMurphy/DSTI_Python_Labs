
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/fruit_start');
    console.log('http://' + document.domain + ':' + location.port + '/fruit_start');

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (msg.number == 0)
        {
            result_string = '<p> Fruit Detected </p>';
            setTimeout(function(){
                window.location.href = "/thumb_video";
            }, 2000);
        }
        else if (msg.number == 1) {
            result_string = '<p> Fruit Detected </p>'
            setTimeout(function(){
                window.location.href = "/thumb_video";
            }, 2000);
        } else {
            result_string = '<p> No fruit detected </p>'
            setTimeout(function(){
                window.location.href = "/";
            }, 2000);
        }
        $('#log').html(result_string);
    });

});