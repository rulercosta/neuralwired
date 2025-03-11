document.addEventListener('DOMContentLoaded', function() {
    // Handle toolbar buttons
    document.querySelectorAll('.toolbar-btn').forEach(button => {
        button.addEventListener('click', function() {
            const command = this.dataset.command;
            const value = this.dataset.value || '';
            
            if (command === 'createLink') {
                const url = prompt('Enter the URL:', 'https://');
                if (url) {
                    document.execCommand(command, false, url);
                }
            } else {
                document.execCommand(command, false, value);
            }
            
            // Focus on the element being edited
            const section = this.closest('.editor-section');
            const input = section.querySelector('input, textarea, [contenteditable="true"]');
            if (input) {
                input.focus();
            }
        });
    });
    
    // Handle font size change
    document.querySelectorAll('.toolbar-select[data-command="fontSize"]').forEach(select => {
        select.addEventListener('change', function() {
            document.execCommand(this.dataset.command, false, this.value);
            
            // Focus on the element being edited
            const section = this.closest('.editor-section');
            const input = section.querySelector('input, textarea, [contenteditable="true"]');
            if (input) {
                input.focus();
            }
        });
    });
    
    // Add new list items
    document.querySelectorAll('.add-item-btn').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const targetList = document.getElementById(targetId);
            const fieldName = this.dataset.name;
            
            const newItem = document.createElement('div');
            newItem.className = 'editable-item';
            newItem.innerHTML = `
                <input type="text" name="${fieldName}" value="" class="editable-input">
                <button type="button" class="remove-item-btn"><i class="fas fa-times"></i></button>
            `;
            
            targetList.appendChild(newItem);
            
            // Add event listener to new remove button
            const newRemoveButton = newItem.querySelector('.remove-item-btn');
            newRemoveButton.addEventListener('click', removeItem);
            
            // Focus the new input
            newItem.querySelector('input').focus();
        });
    });
    
    // Remove list items
    function removeItem() {
        this.closest('.editable-item').remove();
    }
    
    document.querySelectorAll('.remove-item-btn').forEach(button => {
        button.addEventListener('click', removeItem);
    });

    // Make the formatting work better with contenteditable
    document.querySelectorAll('.editable-input, [contenteditable="true"]').forEach(input => {
        input.addEventListener('focus', function() {
            // Store the current selection
            window.lastFocusedInput = this;
        });
    });
    
    // Handle form submission for pages editor
    const pageEditorForm = document.getElementById('page-editor-form');
    if (pageEditorForm) {
        pageEditorForm.addEventListener('submit', function() {
            const contentHtml = document.getElementById('content').innerHTML;
            document.getElementById('content-textarea').value = contentHtml;
        });
    }
});
