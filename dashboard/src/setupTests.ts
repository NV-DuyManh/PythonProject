import '@testing-library/jest-dom';

// JSDOM does not implement the native modal lifecycle; browser QA covers focus and the top layer.
HTMLDialogElement.prototype.showModal = function () { this.open = true; };
HTMLDialogElement.prototype.close = function () { this.open = false; };
