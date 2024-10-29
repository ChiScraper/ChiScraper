%% DATAVIEW_PUBLISHER: start
#dataview-publisher
```dataviewjs
const directory_mdfiles = "mdfiles/";
// u => Entry still needs to be evaluated
// r => Paper should be read
// d => Paper should be downloaded
// D => Paper has been downloaded
// - => Paper is not relevant
const task_status = "u";
const config_tag = "";

// Collect a complete list of papers meeting the task_status and config_tag condition
let pages = dv.pages().filter(
    p => p.file.path.startsWith(directory_mdfiles)
).filter(
    p => (task_status && p.file.tasks.filter(t => t.task_status === task_status).length > 0) || (!task_status)
).filter(
    p => (config_tag && p?.config_tags?.contains(config_tag)) || (!config_tag)
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