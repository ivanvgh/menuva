// ✅ Quantity control — accessible globally
function changeQty(id, delta) {
  const input = document.getElementById(`qty_${id}`);
  if (!input) return;
  const current = parseInt(input.value || '0', 10);
  const newValue = Math.max(0, current + delta);
  input.value = newValue;
}
