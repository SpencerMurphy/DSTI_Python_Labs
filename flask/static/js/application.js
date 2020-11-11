
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/start');
    console.log('http://' + document.domain + ':' + location.port + '/start');

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        if (msg.number == 0)
        {
            result_string = '<p> Thumb UP selected </p>';
            setTimeout(function(){
                window.location.href = "/ticket_printing";
            }, 2000);
        }
        else if (msg.number == 1) {
            result_string = '<p> Thumb DOWN selected </p>'
            setTimeout(function(){
                window.location.href = "/";
            }, 2000);
        }
        else if (msg.number == 9){
            result_string = '<p> No fruit Detected</p>';
            setTimeout(function(){
                window.location.href = "/";
            }, 2000);
        }
        else if (msg.number == 10) {
            result_string = '<p> Tomato Detected </p>'
            setTimeout(function(){
                window.location.href = "/thumb_video/tomato";
            }, 2000);
        } 
        else if (msg.number == 11) {
            result_string = '<p> Apple detected </p>'
            setTimeout(function(){
                window.location.href = "/thumb_video/apple";
            }, 2000);
        }
        else if (msg.number == 12) {
            result_string = '<p> Banana detected </p>'
            setTimeout(function(){
                window.location.href = "/thumb_video/banana";
            }, 2000);
        }
        else if (msg.number == 13) {
            result_string = '<p> Mango detected </p>'
            setTimeout(function(){
                window.location.href = "/thumb_video/mango";
            }, 2000);
        }
        else if (msg.number == 14) {
            result_string = '<p> Several fruits detected </p>'
            setTimeout(function(){
                window.location.href = "/";
            }, 2000);
        }
        else {
            result_string = '<p> No selection found </p>'
            setTimeout(function(){
                window.location.href = "/fruit_manual_choice";
            }, 2000);
        }
        $('#log').html(result_string);
    });

});