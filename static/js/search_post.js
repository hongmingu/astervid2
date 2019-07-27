$(function () {
    if ($('#search_word').html() === '') {
        $('#content_result').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/search/post/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end result</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div class="row div_base" id="post_wrapper_' + value.id + '">' +
                                '<script defer>' +
                                'post_populate("' + value.id + '", "' + value.obj_type + '")' +
                                '<' + '/script>' +
                                '</div>'
                            $('#content_result').append(appender)

                        })
                    }
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
    }

    $('#more_load').on('click', function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/search/post/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                end_id: $('#end_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end result</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var appender = '<div class="row div_base" id="post_wrapper_' + value.id + '">' +
                                '<script defer>' +
                                'post_populate("' + value.id + '", "' + value.obj_type + '")' +
                                '<' + '/script>' +
                                '</div>'
                            $('#content_result').append(appender)

                        })
                    }

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