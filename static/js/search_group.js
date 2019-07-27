$(function () {
    if ($('#search_word').html() === '') {
        $('#content_result').append('<div class="h4">no results</div>')
    } else {
        $.ajax({
            url: '/re/search/group/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                order: $('#order').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end results</div>')
                    } else {
                        $.each(data.output, function (key, value) {
                            var member = '';
                            $.each(value.member, function (key, value) {
                                member = member + ' ' + value

                            })
                            var path = ''
                            var scheme = window.location.protocol == "https:" ? "https://" : "http://";
                            if (value.obj_type === 'group') {
                                path = scheme + window.location.host + "/group/profile/" + value.id + "/";
                            } else if (value.obj_type === 'solo') {
                                path = scheme + window.location.host + "/solo/profile/" + value.id + "/";
                            }
                            var appender = $('<a href="' + path + '"><div class="search_obj_wrapper clickable">' +
                                '<div class="search_obj_img_wrapper">' +
                                '<img class="search_obj_img" src="' + value.main_photo + '">' +
                                '</div>' +
                                '<div class="search_obj_detail_wrapper">' +
                                '<div class="search_obj_detail_name">' + value.main_name + '</div>' +
                                '<div class="search_obj_detail_explain h5">' + member + '</div>' +
                                '</div>' +
                                '</div>' +
                                '</a>')
                            $('#content_result').append(appender)

                        })
                    }

                    if (data.end === "true") {
                        $('#more_load').addClass('hidden')
                    } else if (data.end === "false") {
                        $('#more_load').removeClass('hidden')
                    }
                    $('#order').html(data.order)
                }


            }
        })
    }

    $('#more_load').on('click', function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/search/group/', type: 'post', dataType: 'json', cache: false,
            data: {
                search_word: $('#search_word').html(),
                order: $('#order').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    //user set
                    if (data.output.length === 0) {
                        $('#content_result').append('<div class="h4">end results</div>')

                    } else {
                        $.each(data.output, function (key, value) {
                            var member = '';
                            $.each(value.member, function (key, value) {
                                member = member + ' ' + value

                            })
                            var path = ''
                            var scheme = window.location.protocol == "https:" ? "https://" : "http://";
                            if (value.obj_type === 'group') {
                                path = scheme + window.location.host + "/group/profile/" + value.id + "/";
                            } else if (value.obj_type === 'solo') {
                                path = scheme + window.location.host + "/solo/profile/" + value.id + "/";
                            }
                            var appender = $('<a href="' + path + '"><div class="search_obj_wrapper clickable">' +
                                '<div class="search_obj_img_wrapper">' +
                                '<img class="search_obj_img" src="' + value.main_photo + '">' +
                                '</div>' +
                                '<div class="search_obj_detail_wrapper">' +
                                '<div class="search_obj_detail_name">' + value.main_name + '</div>' +
                                '<div class="search_obj_detail_explain h5">' + member + '</div>' +
                                '</div>' +
                                '</div>' +
                                '</a>')
                            $('#content_result').append(appender)

                        })
                    }

                    if (data.end === "true") {
                        $('#more_load').addClass('hidden')
                    } else if (data.end === "false") {
                        $('#more_load').removeClass('hidden')
                    }
                    $('#order').html(data.order)
                }


            }
        })
    })


})