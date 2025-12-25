/**
 * Generate a random string consisting of upper‑case, lower‑case letters and digits.
 *
 * @param {number} length - Desired length of the random string.
 * @returns {string} Randomly generated string.
 */
export function randomString(length = 12) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    const charsetLength = charset.length;

    // Use crypto.getRandomValues when available for better randomness
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        const randomValues = new Uint32Array(length);
        crypto.getRandomValues(randomValues);
        for (let i = 0; i < length; i++) {
            result += charset[randomValues[i] % charsetLength];
        }
    } else {
        // Fallback to Math.random (less secure)
        for (let i = 0; i < length; i++) {
            const randomIndex = Math.floor(Math.random() * charsetLength);
            result += charset[randomIndex];
        }
    }
    return result;
}