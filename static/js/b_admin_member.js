$(function () {
    $('#register').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/member/register/',
            type: 'post',
            dataType: 'json',
            cache: false,
            data: {
                solo_id: $('#solo_id_input').val(),
                group_id: $('#group_id_input').val(),
            },
            success: function (data) {
                if (data.res === 1) {
                    if (data.result === 'delete') {
                        alert('deleted')
                        $('#solo_id_input').val('')
                        $('#group_id_input').val('')
                    } else if (data.result === 'create') {
                        alert('created')
                        $('#solo_id_input').val('')
                        $('#group_id_input').val('')
                    } else {
                        alert('res was 1 but failed')
                    }
                } else {
                    alert('failed')
                }
            }
        });
    })
})