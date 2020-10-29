django.jQuery(document).ready(function() {
    // Bind on continent field change
    django.jQuery(':input[name$=branch]').change(function() {
        // Get the field prefix, ie. if this comes from a formset form
        var prefix = django.jQuery(this).getFormPrefix();
        // TODO: 金融機関との連動、暫定対策：一気に複数の空白フォームを作成しておく
        // Clear the autocomplete with the same prefix
        // django.jQuery(':input[name=' + prefix + 'branch]').val(null).trigger('change');
    });
});