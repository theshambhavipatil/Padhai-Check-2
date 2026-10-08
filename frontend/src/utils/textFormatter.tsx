/**
 * Utility to render text with markdown-style formatting
 * - Converts **bold** to <strong>
 * - Converts URLs to clickable links
 */

export function renderFormattedText(text: string): JSX.Element[] {
  const lines = text.split('\n');

  return lines.map((line, lineIndex) => {
    // Split line by **bold** markers and URLs
    let partIndex = 0;

    // Process bold text and URLs
    const processText = (txt: string): (string | JSX.Element)[] => {
      const result: (string | JSX.Element)[] = [];
      let remaining = txt;

      while (remaining.length > 0) {
        // Check for bold text **...**
        const boldMatch = remaining.match(/\*\*(.*?)\*\*/);
        if (boldMatch && boldMatch.index !== undefined) {
          // Add text before bold
          if (boldMatch.index > 0) {
            result.push(...processUrls(remaining.substring(0, boldMatch.index)));
          }
          // Add bold text
          result.push(
            <strong key={`bold-${lineIndex}-${partIndex++}`} className="font-semibold text-gray-900">
              {boldMatch[1]}
            </strong>
          );
          remaining = remaining.substring(boldMatch.index + boldMatch[0].length);
        } else {
          // No more bold text, process remaining for URLs
          result.push(...processUrls(remaining));
          break;
        }
      }
      return result;
    };

    // Process URLs in text
    const processUrls = (txt: string): (string | JSX.Element)[] => {
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const parts: (string | JSX.Element)[] = [];
      let lastIndex = 0;
      let match;

      while ((match = urlRegex.exec(txt)) !== null) {
        // Add text before URL
        if (match.index > lastIndex) {
          parts.push(txt.substring(lastIndex, match.index));
        }
        // Add clickable URL
        parts.push(
          <a
            key={`url-${lineIndex}-${partIndex++}`}
            href={match[0]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            {match[0]}
          </a>
        );
        lastIndex = match.index + match[0].length;
      }

      // Add remaining text
      if (lastIndex < txt.length) {
        parts.push(txt.substring(lastIndex));
      }

      return parts.length > 0 ? parts : [txt];
    };

    const processed = processText(line);

    return (
      <span key={`line-${lineIndex}`}>
        {processed}
        {lineIndex < lines.length - 1 && <br />}
      </span>
    );
  });
}
