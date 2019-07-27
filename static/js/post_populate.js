var post_populate = function post_populate(id, obj_type) {
    $(function () {
        $.ajax({
            url: '/re/post/populate/', type: 'post', dataType: 'json', cache: false,
            data: {
                post_id: id,
                obj_type: obj_type
            },
            success: function (data) {
                if (data.res === 1) {
                    var text = ''
                    if (data.output.text === null) {

                    } else {
                        text = '<div class="pop_text">' + data.output.text + '</div>'
                    }

                    var obj = '<div align="right"><a href="/' + obj_type + '/profile/' + data.output.obj_id + '/"><span class="pop_obj">' + data.output.obj_name + '</span></a></div>'

                    var comment_more_load = '<a href=""><div class="pop_comment_more_load hidden" id="pop_comment_more_load_' + id + '" align="center">more load</div></a>'
                    if (data.output.comment_count > 3) {
                        comment_more_load = '<a href=""><div class="pop_comment_more_load" id="pop_comment_more_load_' + id + '" align="center">more load</div></a>'
                    }

                    var comment_textarea = '<div align="center"><form><div class="input-group input-group-sm">' +
                        '<textarea class="form-control pop_comment_textarea" id="pop_comment_textarea_' + id + '" placeholder="a comment"></textarea>' +
                        '<div class="input-group-btn">' +
                        '<button class="btn btn-default" id="pop_comment_btn_' + id + '">' +
                        '<i class="glyphicon glyphicon-send"></i>' +
                        '</button></div>' +
                        '</div>' +
                        '</form>' +
                        '</div>'
                    var comments = ''
                    var user_id = $('#user_id').html()
                    var post_user_id = data.output.user_id
                    var last_comment_id = ''
                    $.each(data.output.comment_output, function (key, value) {
                        var delete_btn = ''
                        if (value.comment_user_id === user_id || user_id === post_user_id) {
                            delete_btn = '<a href=""><span class="glyphicon glyphicon-remove pop_comment_delete" data-u="' + value.comment_id + '"></span></a>'
                        }
                        comments = comments + '<div id="pop_comment_wrapper_' + value.comment_id + '">' +
                            '<div><a href="/' + value.comment_username + '/"><span class="pop_comment_username">' + value.comment_username + '</span></a></div>' +
                            '<div class="pop_comment_content"><span class="pop_comment_text">' + value.comment_text + '</span><span class="pop_comment_created">' + date_differ(value.comment_created) + '</span>' + delete_btn + '</div>' +
                            '</div>'
                        last_comment_id = value.comment_id
                    })
                    var last_comment = '<div class="hidden" id="last_comment_' + id + '">' + last_comment_id + '</div>'

                    var heart = ''
                    if (data.output.like === 'true') {
                        heart = '<a href=""><span class="pop_heart" id="pop_heart_' + id + '">♥</span></a>'
                    } else {
                        heart = '<a href=""><span class="pop_heart" id="pop_heart_' + id + '">♡</span></a>'
                    }
                    var appender = $('<div id="pop_' + id + '">' +
                        '<div align="right"><a href=""><span class="glyphicon glyphicon-option-horizontal pop_menu"></span></a></div>' +
                        '<div><a href="/' + data.output.username + '/"><span class="pop_username">' + data.output.username + '</span></a></div>' +
                        obj +
                        text +
                        '<div align="right"><span class="pop_gross">' + data.output.gross + '</span><span class="pop_dollar">$</span></div>' +
                        '<div align="right"><span class="pop_date">' + data.output.date + '</span><span class="pop_created">' + date_differ(data.output.created) + '</span></div>' +
                        '<div><div class="pop_like_left"><span class="pop_like_black_heart">♥</span><a href=""><span class="pop_like_count" id="pop_like_count_' + id + '">' + data.output.like_count + '</span></a></div><div class="pop_like_right" align="right">' + heart + '</div></div>' +
                        '<div><span class="pop_comment">comment</span><span class="pop_comment_count">' + data.output.comment_count + '</span></div>' +
                        '<div id="pop_comment_list_' + id + '">' + comments + '</div>' +//여기서 이것의 차일드 중 마지막 값의 uuid 를 이용하여 이것 다음 코멘트를
                        comment_more_load +
                        '<div id="pop_new_comment_list_' + id + '"></div>' +
                        comment_textarea +
                        last_comment +
                        '</div>')
                    appender.find('.pop_like_count').on('click', function (e) {
                        e.preventDefault()
                        $('#clicked_post_id').html(id)
                        $('#modal_post_liking').modal('show')
                    })

                    appender.find('.pop_heart').on('click', function (e) {
                        e.preventDefault()
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        $.ajax({
                            url: '/re/post/like/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                post_id: id,
                            },
                            success: function (s_data) {
                                if (s_data.res === 1) {
                                    var current_count = parseInt($('#pop_like_count_' + id).html())
                                    if (s_data.liked === 'true') {
                                        if ($('#pop_heart_' + id).html() !== '♥') {
                                            $('#pop_heart_' + id).html('♥')
                                        }
                                        $('#pop_like_count_' + id).html(current_count + 1)
                                    } else if (s_data.liked === 'false') {
                                        if ($('#pop_heart_' + id).html() !== '♡') {
                                            $('#pop_heart_' + id).html('♡')
                                        }
                                        $('#pop_like_count_' + id).html(current_count - 1)
                                    }

                                }
                            }
                        })

                    })

                    appender.find('#pop_comment_more_load_' + id).on('click', function (e) {
                        e.preventDefault()
                        $.ajax({
                            url: '/re/comment/more/load/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                post_id: id,
                                last_comment_id: $('#last_comment_' + id).html(),
                            },
                            success: function (s_data) {
                                if (s_data.res === 1) {
                                    var _comment = ''
                                    $.each(s_data.output, function (s_key, s_value) {
                                        var delete_btn = ''
                                        if (s_value.comment_user_id === user_id || user_id === post_user_id) {
                                            delete_btn = '<a href=""><span class="glyphicon glyphicon-remove pop_comment_delete" data-u="' + s_value.comment_id + '"></span></a>'
                                        }
                                        _comment = _comment + '<div id="pop_comment_wrapper_' + s_value.comment_id + '">' +
                                            '<div><a href="/' + s_value.comment_username + '/"><span class="pop_comment_username">' + s_value.comment_username + '</span></a></div>' +
                                            '<div class="pop_comment_content"><span class="pop_comment_text">' + s_value.comment_text + '</span><span class="pop_comment_created">' + date_differ(s_value.comment_created) + '</span>' + delete_btn + '</div>' +
                                            '</div>'
                                    })
                                    var _comment_appender = $(_comment)
                                    _comment_appender.find('.pop_comment_delete').on('click', function (e) {
                                        e.preventDefault()
                                        var delete_comment_id = $(this).attr('data-u')
                                        $.ajax({
                                            url: '/re/comment/delete/', type: 'post', dataType: 'json', cache: false,
                                            data: {
                                                post_id: id,
                                                comment_id: delete_comment_id,
                                            },
                                            success: function (ss_data) {
                                                if (ss_data.res === 1) {
                                                    $('#pop_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                                }
                                            }
                                        })
                                    })
                                    $('#pop_comment_list_' + id).append(_comment_appender)

                                    if (s_data.last === null) {
                                        if (!($('#pop_comment_more_load_' + id).hasClass('hidden'))) {
                                            $('#pop_comment_more_load_' + id).addClass('hidden')
                                        }
                                        $('#last_comment_' + id).html('')

                                    } else {
                                        if ($('#pop_comment_more_load_' + id).hasClass('hidden')) {
                                            $('#pop_comment_more_load_' + id).removeClass('hidden')
                                        }
                                        $('#last_comment_' + id).html(s_data.last)
                                    }
                                }
                            }
                        })
                    })

                    appender.find('.pop_comment_delete').on('click', function (e) {
                        e.preventDefault()
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        var delete_comment_id = $(this).attr('data-u')
                        $.ajax({
                            url: '/re/comment/delete/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                post_id: id,
                                comment_id: delete_comment_id,
                            },
                            success: function (s_data) {
                                if (s_data.res === 1) {
                                    $('#pop_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                }
                            }
                        })
                    })

                    appender.find('.pop_menu').on('click', function (e) {
                        e.preventDefault()
                        $('#clicked_post_id').html(id)
                        $('#modal_pop_menu').modal('show')
                    })

                    appender.find('#pop_comment_textarea_' + id).on('keypress', function (e) {
                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }

                        if (e.keyCode == 13 && !e.shiftKey) {
                            var text = $('#pop_comment_textarea_' + id).val()
                            text = text.trim()
                            if (text === '') {
                                return false;
                            }
                            if (1000 < text.length) {
                                alert('too long')
                                return false;
                            }
                            $.ajax({
                                url: '/re/comment/add/', type: 'post', dataType: 'json', cache: false,
                                data: {
                                    post_id: id,
                                    text: text,
                                },
                                success: function (s_data) {
                                    if (s_data.res === 1) {
                                        var _comment_appender = $('<div id="pop_new_comment_wrapper_' + s_data.comment_id + '">' +
                                            '<div class="pop_new_comment_content"><span class="pop_new_comment_text">' + s_data.comment_text + '</span><a href=""><span class="glyphicon glyphicon-remove pop_new_comment_delete" data-u="' + s_data.comment_id + '"></span></a></div>' +
                                            '</div>');

                                        _comment_appender.find('.pop_new_comment_delete').on('click', function (e) {
                                            e.preventDefault()
                                            var delete_comment_id = $(this).attr('data-u')
                                            $.ajax({
                                                url: '/re/comment/delete/',
                                                type: 'post',
                                                dataType: 'json',
                                                cache: false,
                                                data: {
                                                    post_id: id,
                                                    comment_id: delete_comment_id,
                                                },
                                                success: function (ss_data) {
                                                    if (ss_data.res === 1) {
                                                        $('#pop_new_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                                    }
                                                }
                                            })
                                        })
                                        $('#pop_new_comment_list_' + id).append(_comment_appender)
                                        $('#pop_comment_textarea_' + id).val('')
                                    }
                                }
                            })

                        }
                    })

                    appender.find('#pop_comment_btn_' + id).on('click', function (e) {
                        e.preventDefault()

                        if ($('#user_id').html() === '') {
                            $('#modal_need_login_pop').modal('show')
                            return false;
                        }
                        var text = $('#pop_comment_textarea_' + id).val()
                        text = text.trim()
                        if (text === '') {
                            return false;
                        }
                        if (1000 < text.length) {
                            alert('too long')
                            return false;
                        }
                        $.ajax({
                            url: '/re/comment/add/', type: 'post', dataType: 'json', cache: false,
                            data: {
                                post_id: id,
                                text: text,
                            },
                            success: function (s_data) {

                                if (s_data.res === 1) {
                                    var _comment_appender = $('<div id="pop_new_comment_wrapper_' + s_data.comment_id + '">' +
                                        '<div class="pop_new_comment_content"><span class="pop_new_comment_text">' + s_data.comment_text + '</span><a href=""><span class="glyphicon glyphicon-remove pop_new_comment_delete" data-u="' + s_data.comment_id + '"></span></a></div>' +
                                        '</div>');

                                    _comment_appender.find('.pop_new_comment_delete').on('click', function (e) {
                                        e.preventDefault()
                                        var delete_comment_id = $(this).attr('data-u')
                                        $.ajax({
                                            url: '/re/comment/delete/', type: 'post', dataType: 'json', cache: false,
                                            data: {
                                                post_id: id,
                                                comment_id: delete_comment_id,
                                            },
                                            success: function (ss_data) {
                                                if (ss_data.res === 1) {
                                                    $('#pop_new_comment_wrapper_' + delete_comment_id).replaceWith('<div class="h5">removed</div>')
                                                }
                                            }
                                        })
                                    })
                                    $('#pop_new_comment_list_' + id).append(_comment_appender)
                                    $('#pop_comment_textarea_' + id).val('')
                                }
                            }
                        })

                    })

                    $('#post_wrapper_' + id).append(appender)
                }
            }
        })
    })
}

$(function () {
    $("#modal_pop_menu").on("shown.bs.modal", function () {
        var clicked_post = $('#clicked_post_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/post/' + clicked_post + '/';
        $('#modal_pop_menu_input').val(path).select();
    }).on("hidden.bs.modal", function () {
        $('#clicked_post_id').html('')
        $('#modal_pop_menu_input').val('')
    });

    $('#modal_pop_menu_copy').click(function (e) {
        e.preventDefault()
        var clicked_post = $('#clicked_post_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/post/' + clicked_post + '/';
        $('#modal_pop_menu_input').val(path).select();
        document.execCommand('Copy')
    })
    $('#modal_pop_menu_locate').click(function (e) {
        e.preventDefault()
        var clicked_post = $('#clicked_post_id').html()
        var scheme = window.location.protocol == "https:" ? "https" : "http";
        var path = scheme + '://' + window.location.host + '/post/' + clicked_post + '/';
        location.href = path
    })
})

$(function () {
    $("#modal_post_liking").on("shown.bs.modal", function () {
        var height = $(window).height();
        $('.modal-body').css('max-height', height - 120);
        $(window).on('resize', function () {

            if ($(window).height() != height) {
                height = $(window).height();
                $('.modal-body').css('max-height', height - 120);
            }
        });
        var post_id = $('#clicked_post_id').html()

        $.ajax({
            url: '/re/post/like/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                post_id: post_id,
                next_id: $('#post_liking_next_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_post_liking_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#post_liking_next_id').html('')
                    $('#modal_post_liking_more').addClass('hidden')
                } else {
                    $('#post_liking_next_id').html(data.next)
                    $('#modal_post_liking_more').removeClass('hidden')
                }

            }
        })
    }).on("hidden.bs.modal", function () {
        $('#modal_post_liking_list').empty()
        $('#post_liking_next_id').html('')
        $('#clicked_post_id').html('')
    });

    $('#modal_post_liking_more').click(function (e) {
        e.preventDefault()
        $.ajax({
            url: '/re/post/like/list/', type: 'post', dataType: 'json', cache: false,
            data: {
                post_id: post_id,
                next_id: $('#post_liking_next_id').html()
            },
            success: function (data) {
                if (data.res === 1) {
                    $.each(data.output, function (key, value) {
                        var appender = '<div class="modal_unit_wrapper"><a href="/' + value.username + '/">\n' +
                            '<img class="modal_img" src="' + value.photo + '">\n' +
                            '<span class="modal_username">' + value.username + '</span>\n' +
                            '</a></div>'
                        $('#modal_post_liking_list').append(appender)
                    })
                }
                if (data.next === null) {
                    $('#post_liking_next_id').html('')
                    $('#modal_post_liking_more').addClass('hidden')
                } else {
                    $('#post_liking_next_id').html(data.next)
                    $('#modal_post_liking_more').removeClass('hidden')
                }

            }
        })
    })
})