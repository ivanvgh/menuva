document.addEventListener('DOMContentLoaded', function() {
  // Listen globally for select2 selection events
  document.body.addEventListener('select2:select', function(e) {
    const select = e.target;
    if (!select.name.endsWith('-item')) return;

    const priceInputName = select.name.replace('-item', '-unit_price');
    const priceInput = document.querySelector(`[name="${priceInputName}"]`);
    if (!priceInput) return;

    const selectedData = e.detail && e.detail.data;
    if (selectedData && selectedData.base_price !== undefined && selectedData.base_price !== null) {
      priceInput.value = selectedData.base_price;
    }
  });
});
