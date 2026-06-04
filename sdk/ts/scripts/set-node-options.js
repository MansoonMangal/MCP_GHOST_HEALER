/**
 * Postinstall: prepend ghost-healer-ts/auto-activate to NODE_OPTIONS for zero-change activation.
 */
'use strict';
const path = require('path');
const flag = '--require ghost-healer-ts/auto-activate';
const existing = process.env.NODE_OPTIONS || '';
if (!existing.includes('ghost-healer-ts/auto-activate')) {
  process.env.NODE_OPTIONS = existing ? `${existing} ${flag}` : flag;
  console.log('[GHOST] NODE_OPTIONS set for auto-activation:', flag);
}
