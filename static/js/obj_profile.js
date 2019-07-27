$(function () {
    var obj_type = $('#obj_type').html()
    $('#follow').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/' + obj_type + '/follow/', type: 'post', dataType: 'json', cache: false,
            data: {
                obj_id: $('#obj_id').html(),
            },
            success: function (data) {
                if (data.res === 1) {
                    if (data.result === 'follow') {
                        $('#follow').html('<span class="now_following">following <span class="glyphicon glyphicon-ok"></span></span>')
                        var count = $('#follower_count').html()
                        $('#follower_count').html(parseInt(count) + 1)
                    } else if (data.result === 'cancel') {
                        $('#follow').html('<span class="now_unfollow">follow</span>')
                        var count = $('#follower_count').html()
                        $('#follower_count').html(parseInt(count) - 1)
                    }
                }

            }
        })
    })
})