<script>
  import { fade, fly } from 'svelte/transition';
  import { statsStore, detectionsStore, spectrogramStore, mostRecentStore, fetchFlickrBirdImage, displayDate } from './store.js';
  import { plotBars, plotCells, plotSpectrogram } from './plots.js'
  import { DateInput } from 'date-picker-svelte'

  function tsToDateString(timestamp){
    console.log(timestamp)
    const d = new Date(timestamp * 1000)
    console.log(d)
    return (
      d.toLocaleString()
    );
  }

  let data, barDiv, cellDiv, specDiv;

  $: {
    barDiv?.firstChild?.remove(); // remove old chart, if any
    barDiv?.append(plotBars($detectionsStore)); // add the new chart
    cellDiv?.firstChild?.remove(); // remove old chart, if any
    cellDiv?.append(plotCells($detectionsStore)); // add the new chart
    specDiv?.firstChild?.remove(); // remove old chart, if any
    specDiv?.append(plotSpectrogram($spectrogramStore)); // add the new chart
  }
</script>

<main>
  <h1>BirdFront</h1>
  <div id="plots">
    <h3>Statistik</h3>
    <span id="stats">
      <h4> Heute: {$statsStore?.today}</h4>
      <h4> Letzte Stunde: {$statsStore?.last_hour}</h4>
      <h4> Anzahl Spezies (Heute): {$statsStore?.total_unique_species_today}</h4>
      <h4> Anzahl Spezies (Gesamt): {$statsStore?.total_unique_species}</h4>
    </span>
    <h3 id="dateheader">Top 10 Vögel am <DateInput
      id="day"
      required
      bind:value={$displayDate}
      format="dd.MM.yyyy"
      closeOnSelection=true
      --date-input-width="90px"
    />
    </h3>
    {#if $detectionsStore}
      <div in:fade class="plotStyles" bind:this={barDiv} role="img"></div>
      <div in:fade class="plotStyles" bind:this={cellDiv} role="img"></div>
    {:else}
      <div class="plotStyles" ></div>
      <div class="plotStyles" ></div>
    {/if}
    <h3>Letzter Vogel</h3>
    {#if $mostRecentStore.length > 0}
      <div in:fade id="most_recent">
        {#await fetchFlickrBirdImage($mostRecentStore[0]?.scientific_name)}
          <div id="most_recent_image" style:height="75px" style:width="75px"></div>
        {:then image}
          <img id="most_recent_image" src={image} alt="A picture of {data?.most_recent?.scientific_name}">
        {/await}
        <div id="common_name">{$mostRecentStore[0]?.common_name}</div>
        <div id="scientific_name">{$mostRecentStore[0]?.scientific_name}</div>
        <div id="confidence">Sicherheit: {($mostRecentStore[0]?.confidence * 100).toFixed(1)} %</div>
        <div id="recording_date">Datum: {tsToDateString($mostRecentStore[0]?.recording_date)}</div>
        {#if $spectrogramStore}
          <div id="spectrogram" class="plotStyles" bind:this={specDiv} role="img"></div>
        {:else}
          <div id="spectrogram" class="plotStyles"></div>
        {/if}
      </div>
      <h3>Letzten 5 Vögel</h3>
      {#each $mostRecentStore?.slice(1, $mostRecentStore?.length) as recent}
        <div class="recent_detection">
          {#await fetchFlickrBirdImage(recent.scientific_name)}
            <div id="most_recent_image" style:height="75px" style:width="75px"></div>
          {:then image}
            <img id="most_recent_image" src={image} alt="A picture of {recent.scientific_name}">
          {/await}
          <div id="common_name">{recent.common_name}</div>
          <div id="scientific_name">{recent.scientific_name}</div>
          <div id="confidence">Sicherheit: {(recent.confidence * 100).toFixed(1)} %</div>
        </div>
      {/each}

    {/if}
  </div>
</main>

<style>
  #dateheader {
    display: flex;
    flex-direction: row;
    gap: 10px;
    justify-self: center;
    align-items: center;
  }
  :global(#dateheader input#day) {
    text-align: center;
  }
  #most_recent {
    height: 100px;
    /* height: 500px; */
    display: grid;
    grid-template-areas:
        "image common_name"
        "image scientific_name"
        "image confidence"
        "recording_date recording_date"
        "spectrogram spectrogram";
    grid-template-rows: 1em 1em 1em 1em auto;
    grid-template-columns: auto auto;
    gap: 10px;
    align-items: center;
  }
  .recent_detection {
    height: 100px;
    display: grid;
    grid-template-areas:
        "image common_name"
        "image scientific_name"
        "image confidence";
    grid-template-rows: 1em 1em 1em auto;
    grid-template-columns: auto auto;
    gap: 10px;
    align-items: center;
    align-content: center;
  }
  #most_recent_image {
      grid-area: image;
      justify-self: end;
      align-self: center;
  }
  #common_name {
      grid-area: common_name;
      justify-self: start;
  }
  #scientific_name {
      grid-area: scientific_name;
      justify-self: start;
      font-style: italic
  }
  #confidence {
      grid-area: confidence;
      justify-self: start;
  }
  #spectrogram {
      grid-area: spectrogram;
      justify-self: center;
  }
  #recording_date {
      grid-area: recording_date;
      justify-self: center;
  }
  .plotStyles {
  }
  #stats {
    display: grid;
    grid-template-columns: auto auto auto auto;
    grid-template-rows: auto;
    grid-gap: 40px
  }
  #plots {
    display: grid;
    grid-template-columns: auto;
    grid-template-rows: auto auto;
  }
</style>
