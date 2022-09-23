// (function( $ ){
//   $.fn.animateProgress = function(progress, callback) {
//     return this.each(function() {
//       $(this).animate({
//         width: progress+'%'
//       }, {
//         duration: 2000,
//
//         easing: 'swing',
//
//         step: function( progress ){
//           var labelEl = $('.ui-label', this),
//               valueEl = $('.value', labelEl);
//
//           if (Math.ceil(progress) < 20 && $('.ui-label', this).is(":visible")) {
//             labelEl.hide();
//           }else{
//             if (labelEl.is(":hidden")) {
//               labelEl.fadeIn();
//             };
//           }
//
//           if (Math.ceil(progress) == 100) {
//             labelEl.text('Done');
//             setTimeout(function() {
//               labelEl.fadeOut();
//             }, 1000);
//           }else{
//             valueEl.text(Math.ceil(progress) + '%');
//           }
//         },
//         complete: function(scope, i, elem) {
//           if (callback) {
//             callback.call(this, i, elem );
//           };
//         }
//       });
//     });
//   };
// })( jQuery );
//
// $(function() {
//   $('#progress_bar .ui-progress .ui-label').hide();
//   $('#progress_bar .ui-progress').css('width', '7%');
//
//   $('#progress_bar .ui-progress').animateProgress(43, function() {
//     $(this).animateProgress(79, function() {
//       setTimeout(function() {
//         $('#progress_bar .ui-progress').animateProgress(100, function() {
//           $('#main_content').slideDown();
//         });
//       }, 2000);
//     });
//   });
//
// });


$(function () {
    var Now = 0;
    var animationDuration = 40000;
    var DesiredWidth = $("#container").width();

    $('#progress_bar .ui-progress').animate({
        width: DesiredWidth
    }, {
        easing:"linear",
        duration: animationDuration,
        //the argument in the step call back function will hold the
        // current position of the animated property - width in this case.
        step: function (currentWidth,fx) {
            Now = Math.round((50/DesiredWidth)*currentWidth);

        }
    });
});
