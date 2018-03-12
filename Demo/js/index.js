var active_state = 1

function uploadSelected(){
    $('#selectForm').hide(100);
    $('#uploadForm').show(100);
}

function selectSelected(){
    $('#uploadForm').hide(100);
    $('#selectForm').show(100);
}

function nextButtonListener(){
    var speed = 200

    if (active_state == 1) {
        $('#panel1').fadeOut(speed).next().delay(speed);
        $('#panel2').fadeIn(speed);
        active_state += 1;
    }

    else if (active_state == 2) {
        $('#panel2').fadeOut(speed).next().delay(speed);
        $('#panel3').fadeIn(speed);

        active_state += 1;
    }

    else {
        $('#next-button').prop('type', 'submit')
    }
}