%% DATAVIEW_PUBLISHER: start
#dataview-publisher
```dataviewjs
const paper_dir = "mdfiles/";
// u => Entry still needs to be evaluated
// r => Paper should be read
// d => Paper should be downloaded
// D => Paper has been downloaded
// - => Paper is not relevant
const status = "u";
const tag = "";

// Collect a complete list of papers meeting the status and tag condition
let pages = dv.pages().filter(
    p => p.file.path.startsWith(paper_dir)
).filter(
    p => (status && p.file.tasks.filter(t => t.status === status).length > 0) || (!status)
).filter(
    p => (tag && p?.config_tags?.contains(tag)) || (!tag)
).sort(
    p => -p.ai_rating
);

// Get the total number of articles
const totalArticles = pages.length;

// Format each article with index/total
let formattedPages = pages.map((p, index) => {
    const rating = typeof p.ai_rating === 'number' ? p.ai_rating : 0;
    const percentage = (rating / 10) * 100;

    return {
        content: [
            `# (${index + 1}/${totalArticles}) ${p.url_pdf}`,
            `\n`,
            `### Rating: ${rating}/10`,
            `\n`,
            `<div style="width: 100%; background-color: #e0e0e0; border-radius: 4px; overflow: hidden;">
                <div style="width: ${percentage}%; background-color: #4caf50; height: 20px; border-radius: 4px;"></div>
            </div>`,
            `\n`,
            `### ${p.title}`,
            `**${p.authors}**`,
            `\n`,
            p?.config_tags?.join(" ") || "",
            `### Abstract:\n${p.abstract}`,
            `\n`,
            p.file.link.toEmbed(),
            `### AI Justification:\n${p.ai_reason || "N/A"}`,
        ].join("\n"),
        rating: rating
    };
});

// Extract the formatted content
const output = formattedPages.map(p => p.content).join("\n");

// Display content
output;
```
%%



%% DATAVIEW_PUBLISHER: end %%