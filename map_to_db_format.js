const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function generateContentHash(content) {
    return crypto.createHash('md5').update(content).digest('hex');
}

function extractAppIdentifier(linkToPost) {
    const match = linkToPost.match(/instagram\.com\/p\/([^\/]+)/);
    return match ? match[1] : null;
}

function mapInstagramToDbFormat() {
    try {
        const inputFile = path.join(__dirname, 'flo_cleaned.json');
        const outputFile = path.join(__dirname, 'flo_db_format.json');
        
        console.log('Reading flo_cleaned.json...');
        const rawData = fs.readFileSync(inputFile, 'utf8');
        const instagramPosts = JSON.parse(rawData);
        
        console.log('Mapping to database format...');
        const dbRecords = [];
        
        instagramPosts.forEach((post, index) => {
            let caption = post.caption || '';
            
            if (post.hashtags && post.hashtags.length > 0) {
                const hashtagsInCaption = post.hashtags.filter(tag => caption.includes(`#${tag}`));
                const missingHashtags = post.hashtags.filter(tag => !caption.includes(`#${tag}`));
                
                if (missingHashtags.length > 0) {
                    const hashtagsText = ' ' + missingHashtags.map(tag => `#${tag}`).join(' ');
                    caption += hashtagsText;
                }
            }
            
            const fullContent = caption;
            const contentHash = generateContentHash(fullContent);
            const appIdentifier = extractAppIdentifier(post.linkToPost);
            
            const dbRecord = {
                pk: `${appIdentifier}#instagram`,
                id: appIdentifier || `instagram_${index}`,
                source: "instagram",
                backlink: post.linkToPost,
                brand: "flo",
                is_processed: false,
                app_identifier: appIdentifier || `instagram_${index}`,
                title: null,
                text: fullContent,
                rating: null,
                language: "undefined",
                country: null,
                author_hint: post.authorFullName,
                created_at: post.postDate,
                fetched_at: new Date().toISOString(),
                content_hash: contentHash
            };
            
            dbRecords.push(dbRecord);
        });
        
        console.log(`Mapped ${dbRecords.length} records to database format`);
        
        fs.writeFileSync(outputFile, JSON.stringify(dbRecords, null, 2));
        console.log(`Database format data saved to ${outputFile}`);
        
        return dbRecords;
        
    } catch (error) {
        console.error('Error mapping to database format:', error.message);
        throw error;
    }
}

if (require.main === module) {
    mapInstagramToDbFormat();
}

module.exports = mapInstagramToDbFormat;
