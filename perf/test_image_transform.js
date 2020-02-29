import http from 'k6/http';
import { check } from 'k6';
import { Rate } from 'k6/metrics';

const maxVU = __ENV.CONCURRENCY || 10;
const wait = __ENV.WAIT || 5;
const warmup = __ENV.WARMUP || 5;
const duration = __ENV.DURATION || 50;
const threshold = __ENV.P95 || 3000;

const failRate = new Rate('failed requests');

export let options = {
  stages: [
    { duration: `${wait}s`, target: 0 },
    { duration: `${warmup}s`, target: maxVU },
    { duration: `${duration}s`, target: maxVU },
  ],
  thresholds: {
    'http_req_duration': [`p(95)<${threshold}`], // 95% of requests must complete below 3s
    'failed requests': ['rate<0.001'],
  }
};

function get_url(img, width, height) {
  return `http://localhost:8888/unsafe/${width}x${height}/${img}`;
}

let src = [
  'sample-very-small.jpg',
  'sample-small.jpg',
  'sample-mid.jpg',
  'sample-large.jpg',
  'sample-very-large.jpg',
];

let cases = [
  // very small
  {url: get_url(src[0], 100, 100), name: 'very-small-to-very-small' },
  {url: get_url(src[0], "orig", "orig"), name: 'very-small-to-orig' },

  // small
  {url: get_url(src[1], 100, 100), name: 'small-to-very-small' },
  {url: get_url(src[1], 480, 400), name: 'small-to-small' },
  {url: get_url(src[1], "orig", "orig"), name: 'small-to-orig' },

  // mid
  {url: get_url(src[2], 100, 100), name: 'mid-to-very-small' },
  {url: get_url(src[2], 480, 400), name: 'mid-to-small' },
  {url: get_url(src[2], 800, 600), name: 'mid-to-mid' },
  {url: get_url(src[2], "orig", "orig"), name: 'mid-to-orig' },

  // // large
  {url: get_url(src[3], 100, 100), name: 'large-to-very-small' },
  {url: get_url(src[3], 480, 400), name: 'large-to-small' },
  {url: get_url(src[3], 800, 600), name: 'large-to-mid' },
  {url: get_url(src[3], 1200, 800), name: 'large-to-large' },
  {url: get_url(src[3], "orig", "orig"), name: 'large-to-orig' },

  // very large
  {url: get_url(src[4], 100, 100), name: 'very-large-to-very-small' },
  {url: get_url(src[4], 480, 400), name: 'very-large-to-small' },
  {url: get_url(src[4], 800, 600), name: 'very-large-to-mid' },
  {url: get_url(src[4], 1200, 800), name: 'very-large-to-large' },
  {url: get_url(src[4], "orig", "orig"), name: 'very-large-to-orig' },
]

export default function() {
  for (let i=0; i < cases.length; i++) {
    const {url, name, expectedTime } = cases[i];
    const res = http.get(url);

    const checks = {};
    checks[`${name} status was 200`] = r => r.status === 200;
    failRate.add(res.status !== 200);

    check(res, checks);
  }
}
