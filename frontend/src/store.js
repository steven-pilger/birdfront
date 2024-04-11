// import { API_URL } from '$env/static/private'
// Figre out how to read this from the env file.
import { writable, derived } from 'svelte/store';

// const API_URL = 'https://birdpihinterweg.stevenpilger.com/api';
const API_URL = 'http://localhost:8000';

export const displayDate = writable(new Date());
export const statsStore = writable()
export const mostRecentStore = writable([])
export const detectionsStore = writable()
export const spectrogramStore = writable()

// Load the most recent on page load.
updateMostRecent()

// On date change fetch the overview data.
displayDate.subscribe(val => {
    fetchOverviewData(val)
})

// Refresh the most recent every 15 seconds.
setInterval(() => {
  updateMostRecent()
}, 15000)

export async function fetchStats() {
    const response = await fetch(`${API_URL}/stats`);
    if (!response.ok) {
        throw new Error('Could not fetch stats');
    }
    return response.json();
}

export async function fetchMostRecent(n) {
    const response = await fetch(`${API_URL}/most_recent?n=${n}`);
    if (!response.ok) {
        throw new Error('Could not fetch most recent');
    }
    return response.json();
}

export async function fetchDetections(date) {
    let URL = `${API_URL}/detections`
    if (date){
        const year = date.getFullYear()
        const month = date.getMonth() + 1  // 0 based months, thus plus 1.
        const day = date.getDate()
        URL += `?date=${year}-${month}-${day}`
    }
    const response = await fetch(URL);
    if (!response.ok) {
        throw new Error('Could not fetch detections');
    }

    return response.json();
}

export async function fetchFlickrBirdImage(scientificName) {
    const response = await fetch(`${API_URL}/birdimage?scientific_name=${scientificName}`);
    if (!response.ok) {
        throw new Error('Could not fetch image from flickr');
    }

    return response.json();
}

export async function fetchSpectrogram(id) {
    const response = await fetch(`${API_URL}/spectrogram?id=${id}`);
    if (!response.ok) {
        throw new Error('Could not fetch spectrogram');
    }

    return response.json();
}

async function updateMostRecent(){
  await fetchMostRecent(6).then(res => {
      mostRecentStore.set(res)
      return res[0]
  }).then(mostRecent => {
    fetchSpectrogram(mostRecent?.id).then(specData =>{
      spectrogramStore.set(specData)
    }).catch()
  })
}

async function fetchOverviewData(date){
  await fetchStats().then(res => statsStore.set(res))
  await fetchDetections(date).then(detections => {
    const dates = detections.map(x => new Date(x.datetime));
    detections.forEach((x, i) => {
      x.datetime = dates[i]
    })
    detectionsStore.set(detections)
  })
}
