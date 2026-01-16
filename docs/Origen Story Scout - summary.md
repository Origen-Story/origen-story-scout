# **Project summary for Origen Story Scout**

## Tool objectives:

#### **Primary**

1. To help comb through all various personalized sources of media and content and surface the signal from the noise. This should include the following capabilities:  
   1. To set preferences for the kind of content to receive. This might include keywords, topics, regions, etc.  
   2. Ingest multiple web-based forms of media, including RSS feeds, newsletters, YouTube videos, podcasts, and content from the decentralized web (Fediverse or AT protocol systems (i.e. Mastodon and BlueSky)  
   3. Scoring the content to surface the most relevant to the user and the user’s audience. This includes keyword matching, but also can include various other scoring bonuses:   
      1. Content creators that validate their work with C2PA manifests or other provenance approaches receive more points than content with non-provenance indicators.  
      2. Stories and links that appear in multiple sources should be surfaced as trending topics.  
      3. Stories that match along several keywords, but are exclusively covered should be flagged for its uniqueness.  
   4. Summarize each of the top nine stories with a 100 word or less blurb. List the next 20 in the ranking without a summary. Include score, trending icons, and starring ability for all stories.  
2. To verify the provenance and authenticity of the content.   
   1. Should check text, image and videos for C2PA manifests (and any other leading open authenticity approaches. SynthID?) and make it possible to review that context from within the tool.   
   2. The “Scout” tool should be flexible to iterate with the swift changing developments of C2PA and other content provenance approaches as the legal and authenticity landscape changes. Staying current on these developments, and using this as a sandbox to test drive implementation is a core requirement of the tool.  
3. To save the stories in a queue for posting, sharing, drafting, etc.  
   1. User should be able to star stories to read and share.  
   2. There should also be a way to tag these saved stories as “read later”, “Share on social”, or “newsletter”, to go in lists of top stories from the week. 

#### **Secondary objectives** 

The following objectives go beyond the core “Scout” functionality but offer improvements that could be valuable either with in this tool, or part of tools that “Scout” communicates with.

##### **DRAFT SOCIAL AND NEWSLETTER CONTENT**

Create a rough draft of social posts and newsletter link summaries based on user selections.

1) First, develop a sense of Matt Ford’s writing style based on past newsletter posts and social posts.  
   2) Apply that to create first draft social posts on what is important in the selected media.

##### **CREATOR COMPENSATION MECHANISM**

The idea is that publications that regularly produce content that appear in the upper rankings, receive stars, and are read and shared on socials/newsletter, should be compensated in some way. 

What I would love is to allocate a monthly budget (Say $20, $50 or $100) and based on the usage statistics, that money is divided out to the most utilized publications. This is currently difficult because there aren’t many automated compensation approaches, but it would be nice to lay the groundwork for this for when the day arrives.

For now we could start with ranking the most used publications and their share of total usage and compensation could be done manually until a viable approach for automated compensation becomes possible.

