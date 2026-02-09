/**
 * Class name utility function for merging Tailwind CSS classes
 * Handles conditional classes and prevents duplicate class names
 * 
 * @param {...(string|undefined|null|false|Object)} inputs - Class names or conditional objects
 * @returns {string} Merged class names
 * 
 * @example
 * cn('px-4 py-2', 'bg-blue-500') // 'px-4 py-2 bg-blue-500'
 * cn('px-4', undefined, 'py-2') // 'px-4 py-2'
 * cn('px-4', false && 'hidden', 'py-2') // 'px-4 py-2'
 * cn({ 'bg-blue-500': true, 'text-white': false }) // 'bg-blue-500'
 */
export function cn(...inputs) {
  const classes = [];
  
  for (const input of inputs) {
    if (!input) continue;
    
    if (typeof input === 'string') {
      classes.push(input);
    } else if (typeof input === 'object' && !Array.isArray(input)) {
      // Handle conditional class objects
      for (const [key, value] of Object.entries(input)) {
        if (value) {
          classes.push(key);
        }
      }
    } else if (Array.isArray(input)) {
      // Recursively handle arrays
      classes.push(cn(...input));
    }
  }
  
  // Join and remove duplicates while preserving order
  const classString = classes.join(' ');
  const uniqueClasses = [...new Set(classString.split(' ').filter(Boolean))];
  
  return uniqueClasses.join(' ');
}

export default cn;
