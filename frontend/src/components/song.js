import update from 'immutability-helper';

/**
 *  * Get the list of todo items.
 *   * @return {Array}
 *    */

export function getAll() {
  return ([
    {
      id: 1,
      videoId: "pM5To8YXHWE",
      title: "Be Me See Me",
      publishedAt: "2015-09-20T15:57:15.000Z",
    },
    {
      id: 2,
      videoId: "I7w9otyiE9g",
      title: "Young Thug - Digits [OFFICIAL AUDIO]",
      publishedAt: "2016-03-25T04:03:28.000Z",
    },
    {
      id: 3,
      videoId: "Tz6OUIjtM6E",
      title:"Young Thug - Best Friend",
      publishedAt: "2015-09-14T21:29:23.000Z",
    }
  ]);
}

export function getItemById(itemId) {
  return getAll().find(item => item.id === itemId);
}

export function updateStatus(items, itemId, completed) {
  let index = items.findIndex(item => item.id === itemId);
  // Returns a new list of data with updated item.
  return update(items, {
    [index]: {
      completed: {$set: completed}
    }
  });
}

/**
 * A counter to generate a unique id for a todo item.
 * Can remove this logic when the todo is created using backend/database logic.
 * @type {Number}
 */
let songCounter = 1;

function getNextId() {
  return getAll().length + songCounter++;
}

/**
 * Adds a new item on the list and returns the new updated list (immutable).
 *
 * @param {Array} list
 * @param {Object} data
 * @return {Array}
 */
export function addToList(list, data) {
  let item = Object.assign({
    id: getNextId()
  }, data);

  return list.concat([item]);
}
