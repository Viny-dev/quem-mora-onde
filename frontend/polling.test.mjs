import { test } from 'node:test';
import assert from 'node:assert/strict';
import { iniciarPolling } from './src/polling.js';
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const response = pecas => ({ok: true, json: async () => ({pecas, pistas: []})});

test('serializa consultas lentas e ignora resposta apos cleanup', async () => {
  let resolve;
  let calls = 0;
  const applied = [];
  globalThis.fetch = () => { calls++; return new Promise(r => { resolve = r; }); };
  const stop = iniciarPolling({url: '/', aplicar: d => applied.push(d.pecas), falhar: assert.fail, intervalo: 5});
  await sleep(25);
  assert.equal(calls, 1);
  stop();
  resolve(response(1));
  await sleep(15);
  assert.deepEqual(applied, []);
  assert.equal(calls, 1);
});

test('recupera de rede, HTTP, JSON e payload invalidos e aplica cada sucesso', async () => {
  let calls = 0;
  let errors = 0;
  const applied = [];
  globalThis.fetch = async () => {
    calls++;
    if (calls === 1) throw new Error('rede');
    if (calls === 2) return {ok: false, status: 500};
    if (calls === 3) return {ok: true, json: async () => {throw new Error('JSON');}};
    if (calls === 4) return {ok: true, json: async () => null};
    return response(calls);
  };
  let stop;
  await new Promise(resolve => {
    stop = iniciarPolling({url: '/', intervalo: 1, aplicar: d => {applied.push(d.pecas); if(applied.length === 2) {stop(); resolve();}}, falhar: () => errors++});
  });
  assert.equal(errors, 4);
  assert.deepEqual(applied, [5, 6]);
});

test('timeout libera consultas futuras e cleanup de montagem anterior nao interfere', async () => {
  let calls = 0;
  let errors = 0;
  globalThis.fetch = (_, {signal, cache}) => {
    assert.equal(cache, 'no-store');
    calls++;
    if (calls === 1) return new Promise((_, reject) => signal.addEventListener('abort', () => reject(new Error('abort'))));
    return Promise.resolve(response(2));
  };
  let stop;
  await new Promise(resolve => {
    stop = iniciarPolling({url: '/', timeout: 5, intervalo: 1, aplicar: () => {stop(); resolve();}, falhar: () => errors++});
  });
  assert.equal(errors, 1);
  assert.equal(calls, 2);
});

test('remontagem aplica novo estado e descarta resposta antiga tardia', async () => {
  let antiga;
  const applied = [];
  globalThis.fetch = () => new Promise(resolve => { antiga = resolve; });
  const stopOld = iniciarPolling({url: '/', aplicar: d => applied.push(d.pecas), falhar: assert.fail});
  stopOld();
  globalThis.fetch = async () => response(9);
  const stopNew = iniciarPolling({url: '/', aplicar: d => applied.push(d.pecas), falhar: assert.fail});
  await sleep(5);
  antiga(response(1));
  await sleep(5);
  stopNew();
  assert.deepEqual(applied, [9]);
});
