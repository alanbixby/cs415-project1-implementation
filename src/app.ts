import chalk from 'chalk'
import got from 'got'
import { setTimeout } from 'timers/promises'

import { RedditResponse } from './index.js'

/* 
  TODO: Use OAuth2 and switch to oauth.reddit.com
  TODO: better error handling
  TODO: rate limit protection (see x-rate-limit headers)
  TODO: potentially move to got.paginate() to better enable the above
  TODO: create a load balancer, 
    > given an array of numbers, create k partitions where the difference of the sum of the greatest partition and the smallest partition are minimized
    > k = ceil(totalSubredditQuery.length / 6570)
      o if the any output partition has a query length > 6570, move their smallest element to the shortest partition
      o if this forces the smallest partition to fail, increase k by 1
*/

export async function* redditStream(
  subreddits: string | string[] = ['all'],
  mode: 'submissions' | 'comments' = 'comments'
) {
  // Input Validation
  if (typeof subreddits === 'string') {
    subreddits = [subreddits]
  }

  if (subreddits.length == 0) {
    throw new Error('No subreddits were provided')
  }

  let currentPage = new Set<string>()
  let lastPage = new Set<string>()
  while (true) {
    console.log(chalk.green('new request'))
    const res = await got<RedditResponse>(
      `https://reddit.com/r/${subreddits.join('+')}/${mode === 'comments' ? mode : 'new'}.json?limit=100`,
      {
        responseType: 'json',
      }
    )
    const children = res.body.data.children
    let overlapped = false
    for (const child of children) {
      currentPage.add(JSON.stringify(child.data.id))
      if (lastPage.has(JSON.stringify(child.data.id))) {
        overlapped = true
        continue
      }
      yield child
    }
    if (!overlapped) {
      console.log(chalk.red('Potentially missed data!'))
    }
    lastPage = currentPage
    currentPage = new Set<string>()
    await setTimeout(1 * 1000)
  }
}

for await (const post of redditStream()) {
  console.log(post.data.id, post.data.author, new Date())
}
