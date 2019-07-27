$(function () {
    var log_type = $('#log_type').html()
    $.ajax({
        url: '/re/log/' + log_type + '/', type: 'post', dataType: 'json', cache: false,
        data: {
            end_id: $('#end_id').html()
        },
        success: function (data) {
            if (data.res === 1) {
                $.each(data.output, function (index, value) {
                    var _obj_id = ''
                    if (log_type === 'charge') {
                        _obj_id = '<div>' +
                            '<span class="log_id_explain">transaction id:</span>' +
                            '<span class="log_id">' + value.obj_id + '</span>' +
                            '</div>'

                    } else if (log_type === 'pay') {
                        _obj_id = '<div>' +
                            '<span class="log_id_explain">post:</span>' +
                            '<a href="/post/' + value.obj_id + '/"><span class="log_id">' + value.obj_id + '</span></a>' +
                            '</div>'

                    }
                    var appender = '<div>' +
                        '<div><span class="log_gross">' + value.gross + '</span></div> ' +
                        _obj_id +
                        '<div align="right"><span class="log_created">' + date_differ(value.created) + '</span></div> ' +
                        '</div>'
                    $('#content').append(appender)
                })


                if (data.end === null) {
                    $('#more_load').addClass('hidden')
                    $('#end_id').html('')
                } else {
                    $('#more_load').removeClass('hidden')
                    $('#end_id').html(data.end)
                }
            }
        }
    })

    $('#more_load').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/log/' + log_type + '/', type: 'post', dataType: 'json', cache: false,
            data: {
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (index, value) {
                        var _obj_id = ''
                        if (log_type === 'charge') {
                            _obj_id = '<div>' +
                                '<span class="log_id_explain">transaction id:</span>' +
                                '<span class="log_id">' + value.obj_id + '</span>' +
                                '</div>'

                        } else if (log_type === 'pay') {
                            _obj_id = '<div>' +
                                '<span class="log_id_explain">post:</span>' +
                                '<a href="/post/' + value.obj_id + '/"><span class="log_id">' + value.obj_id + '</span></a>' +
                                '</div>'

                        }

                        var appender = '<div>' +
                            '<div><span class="log_gross">' + value.gross + '</span></div> ' +
                            _obj_id +
                            '<div align="right"><span class="log_created">' + date_differ(value.created) + '</span></div> ' +
                            '</div>'
                    })


                    if (data.end === null) {
                        $('#more_load').addClass('hidden')
                        $('#end_id').html('')
                    } else {
                        $('#more_load').removeClass('hidden')
                        $('#end_id').html(data.end)
                    }
                }
            }
        })

    })
})