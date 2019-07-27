$(function () {
    $.ajax({
        url: '/re/follow/feed/', type: 'post', dataType: 'json', cache: false,
        data: {
            end_id: $('#end_id').html()
        },
        success: function (data) {
            console.log(data)
            $.each(data.output, function (key, value) {
                console.log(value.obj_type)
                var appender = '<div class="row div_base" id="post_wrapper_' + value.id + '">' +
                    '<script defer>' +
                    '    post_populate("' + value.id + '", "' + value.obj_type + '")' +
                    '<' + '/script>' +
                    '</div>'
                $('#content').append(appender)
            })
            if (data.end === null) {
                $('#more_load').addClass('hidden')
                $('#end_id').html('')
            } else {
                $('#more_load').addClass('hidden')
                $('#end_id').html(data.end)
            }

        }
    })
    $('#more_load').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/follow/feed/', type: 'post', dataType: 'json', cache: false,
            data: {
                end_id: $('#end_id').html()
            },
            success: function (data) {
                $.each(data.output, function (key, value) {
                    var appender = '<div class="row div_base" id="post_wrapper_' + value.id + '">' +
                        '<script defer>' +
                        '    post_populate("' + value.id + '", "' + value.obj_type + '")' +
                        '<' + '/script>' +
                        '</div>'
                    $('#content').append(appender)
                })
                if (data.end === null) {
                    $('#more_load').addClass('hidden')
                    $('#end_id').html('')
                } else {
                    $('#more_load').addClass('hidden')
                    $('#end_id').html(data.end)
                }

            }
        })
    })
})