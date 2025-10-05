const fs = require('fs');
const path = require('path');

function parseFloInsts() {
    try {
        const inputFile = path.join(__dirname, 'flo.insts.json');
        const outputFile = path.join(__dirname, 'flo_cleaned.json');
        
        console.log('Reading flo.insts.json...');
        const rawData = fs.readFileSync(inputFile, 'utf8');
        const data = JSON.parse(rawData);
        
        console.log('Parsing data...');
        const cleanedPosts = [];
        
        if (data.topPosts && Array.isArray(data.topPosts)) {
            data.topPosts.forEach(post => {
                const cleanedPost = {
                    caption: post.caption || '',
                    hashtags: post.hashtags || [],
                    authorFullName: post.ownerFullName || '',
                    linkToPost: post.url || '',
                    postDate: post.timestamp || '',
                    displayUrl: post.displayUrl || '',
                    commentsCount: post.commentsCount || 0,
                    likesCount: post.likesCount || 0
                };
                
                cleanedPosts.push(cleanedPost);
            });
        }
        
        console.log(`Processed ${cleanedPosts.length} posts`);
        
        fs.writeFileSync(outputFile, JSON.stringify(cleanedPosts, null, 2));
        console.log(`Cleaned data saved to ${outputFile}`);
        
        return cleanedPosts;
        
    } catch (error) {
        console.error('Error parsing flo.insts.json:', error.message);
        throw error;
    }
}

if (require.main === module) {
    parseFloInsts();
}

module.exports = parseFloInsts;
