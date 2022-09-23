
function mes() {
    var id = '#message'
    var backHeight = $(document).height();
    var backWidth = $(window).width();
    $('#back').css({ 'width': backWidth, 'height': backHeight });
    $('#back').fadeIn(300);
    $('#back').fadeTo(300, 0.3);
    var winH = $(window).height();
    var winW = $(window).width();
    $(id).css('top', winH / 2 - $(id).height() / 2);
    $(id).css('left', winW / 2 - $(id).width() / 2);
    $(id).fadeIn(300);
};

$(document).ready(function () {
    $('a[name=modal]').click(function (e) {
        e.preventDefault();
        var id = $(this).attr('href');
        var backHeight = $(document).height();
        var backWidth = $(window).width();
        $('#back').css({ 'width': backWidth, 'height': backHeight });
        $('#back').fadeIn(300);
        $('#back').fadeTo(300, 0.3);
        var winH = $(window).height();
        var winW = $(window).width();
        $(id).css('top', winH / 2 - $(id).height() / 2);
        $(id).css('left', winW / 2 - $(id).width() / 2);
        $(id).fadeIn(300);
    });
    $('.window .close').click(function (e) {
        e.preventDefault();
        $('#back, .window').hide();
    });
    $('#back').click(function () {
        $(this).hide();
        $('.window').hide();
    });
});


$(document).ready(function () {
    let inputs = document.querySelectorAll('.input__file');
    inputs.forEach(function (input) {
        let label = input.nextElementSibling;
        let labelVal = label.querySelector('.input__file-button-text');
        input.addEventListener('change', function (e) {
            let countFiles = '';
            if (this.files) {
                countFiles = this.files.length;
                    }

            if (countFiles >= 1) {
                label.querySelector('.input__file-button-text').innerText = 'Выбрано файлов: ' + countFiles;
                if (label.querySelector('#sep')) {
                    label.querySelector('#file_word_sep').style.display="none";
                }
            }
            else {
                label.querySelector('.input__file-button-text').innerText = '';
                if (label.querySelector('#sep')) {
                    label.querySelector('#file_word_sep').style.display = "";
                }
            }



        });
    });
});



$('.select').each(function () {
    const _this = $(this),
        selectOption = _this.find('option'),
        selectOptionLength = selectOption.length,
        selectedOption = selectOption.filter(':selected'),
        duration = 450; // длительность анимации

    _this.hide();
    _this.wrap('<div class="select"></div>');
    $('<div>', {
        class: 'new-select',
        text: _this.children('option:disabled').text()
    }).insertAfter(_this);

    const selectHead = _this.next('.new-select');
    $('<div>', {
        class: 'new-select__list'
    }).insertAfter(selectHead);

    const selectList = selectHead.next('.new-select__list');
    for (let i = 1; i < selectOptionLength; i++) {
        $('<div>', {
            class: 'new-select__item',
            html: $('<span>', {
                text: selectOption.eq(i).text()
            })
        })
            .attr('data-value', selectOption.eq(i).val())
            .appendTo(selectList);
    }

    const selectItem = selectList.find('.new-select__item');
    selectList.slideUp(0);
    selectHead.on('click', function () {
        if (!$(this).hasClass('on')) {
            $(this).addClass('on');
            selectList.slideDown(duration);

            selectItem.on('click', function () {
                let chooseItem = $(this).data('value');

                $('select').val(chooseItem).attr('selected', 'selected');
                selectHead.text($(this).find('span').text());

                selectList.slideUp(duration);
                selectHead.removeClass('on');
            });

        } else {
            $(this).removeClass('on');
            selectList.slideUp(duration);
        }
    });
});
$(document).ready(function () {
    $('.table tr').hover(function () {
        $(this).addClass('hover');
    }, function () {
        $(this).removeClass('hover');
    });

    $('.table tr').click(function () {
        $('.table tr').removeClass('active');
        $(this).addClass('active');
    });
});

$(document).ready(function() { 
    $(".all").on("change", function() {
        var groupId = $(this).data('id');
        $('.one[data-id="' + groupId + '"]').prop("checked", this.checked);
    });

    $(".one").on("change", function() {
        var groupId = $(this).data('id');
        var allChecked = $('.one[data-id="' + groupId + '"]:not(:checked)').length == 0;
        $('.all[data-id="' + groupId + '"]').prop("checked", allChecked);
    });
});

$('.checked_false').click(function() {
    $('input:checked').prop('checked', false);
  });
document.getElementById('date1').max = new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().split("T")[0];
document.getElementById('date2').max = new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().split("T")[0];


