<template>
  <DemoProjectTemplate header="Maximum Flows">
    <template #description>
      <p>
        <a
          href="https://en.wikipedia.org/wiki/Mathematical_optimization"
          target="_blank"
        >Optimization</a> aims to minimize or maximize an objective function (like cost or margin) with given constraints (like capacities or time windows).
      </p>
      <p class="mb-0">
        Some concrete examples include:
      </p>
      <div class="mt-2">
        <v-icon class="mr-3">
          mdi-graph
        </v-icon>Network flows - maximize the margin of a supply chain with given production and delivery capacities
      </div>
      <div class="mt-3">
        <v-icon class="mr-3">
          mdi-truck
        </v-icon>Vehicle routing - minimize the gas consumption of a vehicle with given truck maximum capacity and delivery time windows
      </div>
      <div class="mt-3">
        <v-icon class="mr-3">
          mdi-calendar
        </v-icon>Scheduling - minimize the cost of workforce with given tasks to be completed and workforce schedule preferences
      </div>
      <div class="mt-3">
        <v-icon class="mr-3">
          mdi-cube-outline
        </v-icon>Bin packing - maximize the number of products packed in a truck with given truck capacities and delivery requirements
      </div>
      <p class="mt-5">
        The following demonstrates a maximum flow problem, where the objective is to maximize the total flow from source to sink node with given flow capacities.
      </p>
    </template>
    <template #content>
      <v-row
        class="mt-1 pt-1 mx-0 px-0"
        cols="12"
      >
        <v-col
          xs="12"
          sm="12"
          md="4"
          lg="4"
          xl="4"
        >
          <v-card>
            <v-card-title>
              Information
            </v-card-title>
            <v-card-text>
              Find the flow-maximizing path from the <span style="color: #E57373;"><b>Source</b></span> to the <span style="color: #81C784;"><b>Sink</b></span> node with the given <b>arc</b> capacities.
              <v-col
                class="px-0 py-1 mt-3"
                xs="12"
                sm="12"
                md="12"
                lg="12"
                xl="12"
              >
                <span class="mr-3">{{ $isTouchScreen() ? 'Add node:' : 'Add / remove node:' }}</span>
                <br>
                <kbd>{{ $isTouchScreen() ? 'Tap canvas' : 'Double click' }}</kbd>
              </v-col>
              <v-col
                class="px-0 py-1"
                xs="12"
                sm="12"
                md="12"
                lg="12"
                xl="12"
              >
                <span class="mr-3">New arc:</span>
                <br>
                <kbd>{{ $isTouchScreen() ? 'Tap source and target node' : 'Click source and target node' }}</kbd>
              </v-col>
              <v-col
                class="px-0 py-1"
                xs="12"
                sm="12"
                md="12"
                lg="12"
                xl="12"
              >
                <span class="mr-3">Node / arc settings:</span>
                <br>
                <kbd>{{ $isTouchScreen() ? 'Tap' : 'Click' }}</kbd>
              </v-col>
              <v-col
                class="px-0 py-1"
                xs="12"
                sm="12"
                md="12"
                lg="12"
                xl="12"
              >
                <span class="mr-3">Move graph / node:</span>
                <br>
                <kbd>Drag canvas / node</kbd>
              </v-col>
              <v-row class="my-0 py-0">
                <v-col
                  class="my-4 py-3 pb-0 mb-0"
                  xs="12"
                  sm="12"
                  md="12"
                  lg="12"
                  xl="12"
                >
                  <v-menu
                    v-model="networkMenu"
                    open-on-click
                    bottom
                    offset-x
                    transition="slide-y-transition"
                  >
                    <template #activator="{ on }">
                      <v-btn
                        class="mx-0 px-0"
                        text
                        v-on="on"
                      >
                        Select example
                        <v-icon right>
                          mdi-chevron-right
                        </v-icon>
                      </v-btn>
                    </template>
                    <v-list>
                      <v-list-item
                        v-for="(item, i) in networkItems"
                        :key="i"
                        @click="setNetwork(item.value)"
                      >
                        <v-list-item-title>{{ item.text }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-text
              v-if="warningMessages.length > 0"
            >
              <div
                v-for="(message,i) in warningMessages"
                :key="i"
                class="warning--text mt-2"
              >
                <v-icon color="warning">
                  mdi-alert-circle
                </v-icon>
                {{ message }}
              </div>
            </v-card-text>
            <v-card-actions class="mx-2">
              <v-btn
                class="mb-3"
                outlined
                :loading="loading"
                :disabled="!canRunOptimization"
                @click="runOptimization"
              >
                Optimize
              </v-btn>
              <v-spacer />
              <v-btn
                v-if="!(results === null || loading)"
                class="mb-3"
                text
                @click="toggleResults"
              >
                {{ showResults ? 'Hide results' : 'Show results' }}
                <v-icon>{{ showResults ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
              </v-btn>
            </v-card-actions>
            <v-expand-transition>
              <div v-if="showResults">
                <v-divider />
                <v-card-text>
                  <p class="my-0 mt-2">
                    <span class="subtitle-1 pt-3">Optimal flow:</span>
                    <br>
                    <span class="title">{{ results.optimalFlow }}</span>
                  </p>
                  <p class="my-0 mt-2">
                    <span class="subtitle-1 mt-2">Source side minimum cut: </span>
                    <br>
                    <v-chip
                      v-for="id in results.sourceMinCut"
                      :key="id"
                      small
                      @mouseover="selectNode(id)"
                      @mouseleave="unselectNode(id)"
                      @click="toggleNodeSelection(id)"
                    >
                      {{ nodes.find(x => x.id === id).name }}
                    </v-chip>
                  </p>
                  <p class="my-0 mt-3">
                    <span class="subtitle-1 mt-2">Sink side minimum cut: </span>
                    <br>
                    <v-chip
                      v-for="id in results.sinkMinCut"
                      :key="id"
                      small
                      @mouseover="selectNode(id)"
                      @mouseleave="unselectNode(id)"
                      @click="toggleNodeSelection(id)"
                    >
                      {{ nodes.find(x => x.id === id).name }}
                    </v-chip>
                  </p>
                  <v-switch
                    v-model="showResultsZeroFlows"
                    class="pt-6 mt-0 mb-0 pb-0"
                    label="Show zero flows"
                  />
                </v-card-text>
              </div>
            </v-expand-transition>
          </v-card>
        </v-col>
        <v-col
          xs="12"
          sm="12"
          md="8"
          lg="8"
          xl="8"
        >
          <v-card>
            <v-toolbar
              :collapse="!selectedObject"
              top
              short
              style="padding-left: 6px; z-index: 1;"
              elevation="2"
            >
              <v-tooltip top>
                <template #activator="{ on }">
                  <v-btn
                    small
                    icon
                    v-on="on"
                    @click="stageConfig.scale -= 0.1"
                  >
                    <v-icon>mdi-minus</v-icon>
                  </v-btn>
                </template>
                <span>Zoom out</span>
              </v-tooltip>
              <span style="padding-left: 6px;" />
              <v-tooltip top>
                <template #activator="{ on }">
                  <v-btn
                    small
                    icon
                    v-on="on"
                    @click="stageConfig.scale += 0.1"
                  >
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </template>
                <span>Zoom in</span>
              </v-tooltip>
              <v-scale-transition>
                <v-row
                  v-if="selectedObject && selectedObject.objectType === 'node'"
                  class="ml-2 mr-auto pt-2"
                >
                  <v-col
                    cols="5"
                  >
                    <v-text-field
                      v-model="selectedObject.name"
                      label="Name"
                      placeholder="Name of the node"
                      hide-details
                    />
                  </v-col>
                  <v-col
                    cols="5"
                  >
                    <v-select
                      v-model="selectedObject.type"
                      :items="['Normal', 'Source', 'Sink']"
                      label="Type"
                      placeholder="Node type"
                      hide-details
                      :disabled="showResults"
                    />
                  </v-col>
                  <v-col
                    class="my-0 py-0 mx-0 px-0"
                    align-self-start
                    cols="2"
                  >
                    <v-tooltip top>
                      <template #activator="{ on }">
                        <v-btn
                          icon
                          v-on="on"
                          @click="removeNode(selectedObject.id)"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </template>
                      <span>Remove selected node</span>
                    </v-tooltip>
                  </v-col>
                </v-row>
                <v-row
                  v-if="selectedObject && selectedObject.objectType === 'arc'"
                  class="ml-2 mr-auto pt-2"
                >
                  <v-col
                    class="mb-2"
                    cols="10"
                  >
                    <v-slider
                      v-model="selectedObject.capacity"
                      min="0"
                      max="100"
                      :label="$vuetify.breakpoint.smAndUp ? 'Maximum capacity' : ''"
                      :thumb-size="24"
                      thumb-label="always"
                      :thumb-color="arcSelectedColor"
                      track-color="lightgrey"
                      :track-fill-color="arcSelectedColor"
                      :disabled="showResults"
                      hide-details
                    />
                  </v-col>
                  <v-col
                    class="mt-1 py-0 mx-0 px-0"
                    cols="2"
                    align-self-start
                  >
                    <v-tooltip top>
                      <template #activator="{ on }">
                        <v-btn
                          icon
                          v-on="on"
                          @click="removeArc(selectedObject.id)"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </template>
                      <span>Remove selected arc</span>
                    </v-tooltip>
                  </v-col>
                </v-row>
              </v-scale-transition>
            </v-toolbar>
            <v-container
              ref="container"
              v-resize="resizeStage"
              fluid
              align-start
              fill-height
              class="ma-0 pa-0"
            >
              <v-stage
                ref="stage"
                class="ma-0 pa-0"
                :config="{
                  id: 'stage',
                  width: stageConfig.width,
                  height: stageConfig.height,
                  draggable: true,
                  scaleX: stageConfig.scale,
                  scaleY: stageConfig.scale,
                  x: stageConfig.x,
                  y: stageConfig.y
                }"
                @dblclick="handleStageDoubleClick"
                @click="handleStageClick"
              >
                <v-layer
                  ref="nodes"
                >
                  <v-circle
                    v-for="node in nodes"
                    :key="node.id"
                    class="node"
                    :config="{
                      id: node.id,
                      x: node.x,
                      y: node.y,
                      scaleX: (isObjectSelected(node.id) || (arcSuggestion && arcSuggestion.endNodeId === node.id)) || draggingNodeId === node.id ? 1.15 : 1,
                      scaleY: (isObjectSelected(node.id) || (arcSuggestion && arcSuggestion.endNodeId === node.id)) || draggingNodeId === node.id ? 1.15 : 1,
                      fill: getNodeFill(node),
                      radius: nodeRadius,
                      stroke: 'grey',
                      strokeWidth: 1,
                      shadowColor: 'black',
                      shadowBlur: 3,
                      shadowOpacity: 0.0,
                      draggable: true,
                      hitStrokeWidth: 30
                    }"
                    @click="handleNodeClick"
                    @dblclick="handleNodeDoubleClick"
                    @dragstart="handleNodeDragStart"
                    @dragmove="handleNodeDrag"
                    @dragend="handleNodeDragEnd"
                    @mouseenter="handleNodeMouseEnter"
                    @mouseleave="handleNodeMouseLeave"
                    @touchstart="handleNodeTouchStart"
                    @touchmove="handleNodeDrag"
                    @touchend="handleNodeDragEnd"
                  />
                </v-layer>
                <v-layer
                  ref="arcs"
                >
                  <v-arrow
                    v-if="getArcSuggestion !== null"
                    :config="{
                      id: getArcSuggestion.id,
                      points: getArcSuggestion.points,
                      stroke: arcSelectedColor,
                      strokeWidth: 2,
                      tension: 0.6,
                      dash: [6, 3]
                    }"
                  />
                  <v-arrow
                    v-for="(arc, i) in getArcs"
                    :key="i"
                    :config="{
                      id: arc.id,
                      points: arc.points,
                      stroke: isObjectSelected(arc.id) ? arcSelectedColor : '#212121',
                      strokeWidth: isObjectSelected(arc.id) ? 3 : (arc.flow ? 1.5 + arc.flow / 10 : 1.5),
                      opacity: (showResults && !showResultsZeroFlows && !arc.flow && !isObjectSelected(arc.id)) ? 0 : 1,
                      tension: 0.6,
                      hitStrokeWidth: $isTouchScreen() ? 30 : 20,
                      listening: listenArcs
                    }"
                    @click="handleArcClick"
                    @touchstart="handleArcClick"
                  />
                </v-layer>
                <v-layer
                  ref="text"
                >
                  <v-text
                    v-for="arc in getArcs"
                    :key="arc.id"
                    :config="{
                      id: arc.id,
                      text: getArcText(arc),
                      fontSize: arc.flow !== null ? Math.min(Math.max(arc.flow, 10), 32) : 16,
                      opacity: (showResults && !showResultsZeroFlows && !arc.flow) ? 0 : 1,
                      x: arc.points.length > 4 ? arc.points[2] : (arc.points[0] + arc.points[2]) / 2,
                      y: arc.points.length > 4 ? arc.points[3] : (arc.points[1] + arc.points[3]) / 2 + 2,
                    }"
                    @click="handleArcClick"
                    @touchstart="handleArcClick"
                  />
                  <v-text
                    v-for="node in nodes"
                    :key="node.id"
                    :config="{
                      id: node.id,
                      text: `${node.name}`,
                      fontSize: 12,
                      x: node.x - 3 * node.name.length,
                      y: node.y - 4,
                      draggable: true,
                      listening: false,
                    }"
                    @click="handleNodeClick"
                    @dblclick="handleNodeDoubleClick"
                    @dragstart="handleNodeDragStart"
                    @dragmove="handleNodeDrag"
                    @dragend="handleNodeDragEnd"
                    @mouseenter="handleNodeMouseEnter"
                    @mouseleave="handleNodeMouseLeave"
                  />
                </v-layer>
              </v-stage>
            </v-container>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </DemoProjectTemplate>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import DemoProjectTemplate from '@/components/DemoProjects/DemoProjectTemplate'
const width = window.innerWidth
const height = Math.max(Math.min(window.innerHeight * 1 - 128 * 3 - 16 * 4, 1400), 350)
export default {
  name: 'MaximumFlows',
  components: {
    DemoProjectTemplate
  },
  data: () => ({
    breakpointDefaultScales: {
      xs: 0.7,
      sm: 1.0,
      md: 1.0,
      lg: 1.2,
      xl: 1.25
    },
    stageConfig: {
      width: width,
      height: height,
      scale: 1.0,
      x: 0,
      y: 0
    },
    runningId: 0,
    selectedObject: null,
    arcs: [],
    arcSuggestion: null,
    arcSelectedColor: '#F4511E',
    listenArcs: true,
    nodes: [],
    nodeRadius: 25,
    draggingNodeId: null,
    loading: false,
    showResults: false,
    showResultsZeroFlows: false,
    results: null,
    networkItems: [
      { text: 'Small (default)', value: 'small' },
      { text: 'Medium', value: 'medium' },
      { text: 'Large', value: 'large' }
    ],
    networkMenu: false
  }),
  computed: {
    getArcSuggestion () {
      if (this.arcSuggestion !== null) {
        return {
          id: this.getArcId(this.arcSuggestion.startNodeId, this.arcSuggestion.endNodeId),
          points: this.getArcPoints(this.arcSuggestion.startNodeId, this.arcSuggestion.endNodeId)
        }
      } else {
        return null
      }
    },
    getArcs () {
      const newArcs = []
      this.arcs.forEach(arc => {
        newArcs.push({
          ...arc,
          points: this.getArcPoints(arc.startNodeId, arc.endNodeId)
        })
      })
      return newArcs
    },
    sinkNodes () {
      return this.nodes.filter(x => x.type === 'Sink')
    },
    sourceNodes () {
      return this.nodes.filter(x => x.type === 'Source')
    },
    canRunOptimization () {
      return (this.sinkNodes.length > 0) && (this.sourceNodes.length > 0)
    },
    warningMessages () {
      const messages = []
      if (this.sinkNodes.length !== 1) {
        messages.push('You must have exactly one sink node!')
      }
      if (this.sourceNodes.length !== 1) {
        messages.push('You must have exactly one source node!')
      }
      return messages
    },
    ...mapGetters(['getResults'])
  },
  watch: {
    nodes () {
      if (this.showResults) {
        this.removeResults()
      }
    },
    arcs () {
      if (this.showResults) {
        this.removeResults()
      }
    },
    sinkNodes (newVal, oldVal) {
      if (newVal.length > 1) {
        oldVal[0].type = 'Normal'
      }
    },
    sourceNodes (newVal, oldVal) {
      if (newVal.length > 1) {
        oldVal[0].type = 'Normal'
      }
    },
    warningMessages (newVal, oldVal) {
      if (newVal.length) {
        this.showResults = false
      }
    }
  },
  mounted () {
    this.setNetwork('small')
    const breakpointName = this.$vuetify.breakpoint.name
    this.stageConfig.scale = breakpointName ? this.breakpointDefaultScales[breakpointName] : 1.0
  },
  methods: {
    resizeStage () {
      const container = this.$refs.container
      if (!container) {
        return
      }
      // Resize height only if we have changed width as well
      if (this.stageConfig.width !== container.offsetWidth) {
        this.stageConfig.width = container.offsetWidth
        const multiplier = this.$vuetify.breakpoint.mdAndUp ? 1 : 2 / 3
        this.stageConfig.height = Math.max(Math.min(window.innerHeight * multiplier - 128 * 3 - 16 * 4, 1400), 350)
      }
    },
    handleStageDoubleClick (e) {
      if (this.selectedObject === null && e.target.id() === 'stage') {
        const stage = this.$refs.stage.getNode()
        const pointer = stage.getPointerPosition()
        this.addNode((pointer.x - stage.x()) / this.stageConfig.scale, (pointer.y - stage.y()) / this.stageConfig.scale)
        this.selectedObject = this.nodes.slice(-1)[0]
      }
    },
    handleStageClick (e) {
      if (this.selectedObject !== null && e.target.id() === 'stage') {
        this.selectedObject = null
      }
    },
    handleNodeClick (e) {
      if (!this.arcSuggestion) {
        this.toggleNodeSelection(e.target.id())
      } else {
        this.addArcFromSuggestion()
      }
    },
    handleNodeDoubleClick (e) {
      if (this.arcSuggestion === null && !this.$isTouchScreen()) {
        this.removeNode(e.target.id())
      }
    },
    handleNodeMouseEnter (e) {
      const endNodeId = e.target.id()
      if (this.selectedObject === null) {
        return null
      }
      const somethingSelected = this.selectedObject !== null
      const isNodeSelected = this.selectedObject.objectType === 'node'
      const noArcExists = !this.arcExists(this.selectedObject.id, endNodeId)
      const isNotEndNode = !this.isObjectSelected(endNodeId)
      const isNotFromSink = this.sinkNodes.length ? this.selectedObject.id !== this.sinkNodes[0].id : true
      const isNotToSource = this.sourceNodes.length ? endNodeId !== this.sourceNodes[0].id : true
      if (somethingSelected && isNodeSelected && noArcExists && isNotEndNode && isNotFromSink && isNotToSource) {
        this.setArcSuggestion(this.selectedObject.id, endNodeId)
      }
      this.listenArcs = false
    },
    handleNodeMouseLeave (e) {
      this.arcSuggestion = null
      this.listenArcs = true
    },
    handleNodeDragStart (e) {
      this.draggingNodeId = e.target.id()
      if (!this.isObjectSelected(e.target.id())) {
        this.selectNode(e.target.id())
      }
    },
    handleNodeTouchStart (e) {
      if (this.selectedObject === null) {
        this.draggingNodeId = e.target.id()
        this.selectNode(e.target.id())
      } else if (!this.isObjectSelected(e.target.id())) {
        const endNodeId = e.target.id()
        const isNodeSelected = this.selectedObject.objectType === 'node'
        const noArcExists = !this.arcExists(this.selectedObject.id, endNodeId)
        const isNotEndNode = !this.isObjectSelected(endNodeId)
        const isNotFromSink = this.sinkNodes.length ? this.selectedObject.id !== this.sinkNodes[0].id : true
        const isNotToSource = this.sourceNodes.length ? endNodeId !== this.sourceNodes[0].id : true
        if (isNodeSelected && noArcExists && isNotEndNode && isNotFromSink && isNotToSource) {
          this.addArc(this.selectedObject.id, e.target.id())
          this.selectedObject = this.arcs.slice(-1)[0]
        } else {
          this.draggingNodeId = e.target.id()
          this.selectNode(e.target.id())
        }
      } else {
        this.unselectNode(e.target.id())
      }
    },
    handleNodeDrag (e) {
      if (this.draggingNodeId === e.target.id()) {
        const node = this.nodes.find(x => x.id === this.draggingNodeId)
        node.x = e.target.x()
        node.y = e.target.y()
      }
    },
    handleNodeDragEnd (e) {
      if (this.draggingNodeId === e.target.id()) {
        const node = this.nodes.find(x => x.id === this.draggingNodeId)
        node.x = e.target.x()
        node.y = e.target.y()
        this.draggingNodeId = null
      }
    },
    addNode (x, y, type = 'Normal', name = null) {
      if (!name) {
        name = `Node-${this.runningId + 1}`
      }
      const node = {
        id: `Node-${this.runningId + 1}`,
        name: name,
        x: x,
        y: y,
        objectType: 'node',
        type: type
      }
      this.nodes.push(node)
      this.runningId++
    },
    removeNode (id) {
      const existingNode = this.nodes.find(x => x.id === id)
      const index = this.nodes.indexOf(existingNode)
      this.arcs = this.arcs.filter(x => (x.startNodeId !== id) && (x.endNodeId !== id))
      this.nodes.splice(index, 1)
      if (this.isObjectSelected(id)) {
        this.unselectNode(id)
      }
    },
    selectNode (id) {
      this.selectedObject = this.nodes.find(x => x.id === id)
    },
    unselectNode (id) {
      this.selectedObject = null
    },
    toggleNodeSelection (id) {
      if (this.isObjectSelected(id)) {
        this.unselectNode(id)
      } else {
        this.selectNode(id)
      }
    },
    getNodeFill (node) {
      const showSpecial = (this.isObjectSelected(node.id) || (this.arcSuggestion && this.arcSuggestion.endNodeId === node.id))
      if (node.type === 'Sink') {
        return showSpecial ? '#81C784' : '#C8E6C9'
      } else if (node.type === 'Source') {
        return showSpecial ? '#E57373' : '#FFCDD2'
      } else {
        return showSpecial ? '#64B5F6' : '#B3E5FC'
      }
    },
    handleArcClick (e) {
      const id = e.target.id()
      if (this.isObjectSelected(id)) {
        this.selectedObject = null
      } else {
        this.selectedObject = this.arcs.find(x => x.id === id)
      }
    },
    getArcId (startNodeId, endNodeId) {
      return `${startNodeId}->${endNodeId}`
    },
    getArcPoints (startNodeId, endNodeId) {
      const startNode = this.nodes.find(x => x.id === startNodeId)
      const endNode = this.nodes.find(x => x.id === endNodeId)
      const existingArcs = this.arcs.filter(x => x.id === this.getArcId(endNode.id, startNode.id))
      const points = this.getArcStartEnd(startNode, endNode)
      if (existingArcs.length > 0) {
        const arcCurve = this.getArcCurve(startNode, endNode)
        return [points.arcStart.x, points.arcStart.y, arcCurve.x, arcCurve.y, points.arcEnd.x, points.arcEnd.y]
      } else {
        return [points.arcStart.x, points.arcStart.y, points.arcEnd.x, points.arcEnd.y]
      }
    },
    getArcStartEnd (node1, node2) {
      const dx = node1.x - node2.x
      const dy = node1.y - node2.y
      const angle = Math.atan2(-dy, dx)
      const arcEnd = {
        x: node2.x + -this.nodeRadius * Math.cos(angle + Math.PI),
        y: node2.y + this.nodeRadius * Math.sin(angle + Math.PI)
      }
      const arcStart = {
        x: node1.x + -this.nodeRadius * Math.cos(angle),
        y: node1.y + this.nodeRadius * Math.sin(angle)
      }
      return {
        arcStart: arcStart,
        arcEnd: arcEnd,
        angle: angle
      }
    },
    getArcCurve (node1, node2, curvePower = 20) {
      const points = this.getArcStartEnd(node1, node2)
      const arcCurve = {
        x:
          (points.arcStart.x + points.arcEnd.x) / 2 +
           curvePower * Math.cos(points.angle + Math.PI / 2),
        y:
          (points.arcStart.y + points.arcEnd.y) / 2 +
           curvePower * Math.sin(points.angle - Math.PI / 2)
      }
      return arcCurve
    },
    getExistingArcs (startNodeId, endNodeId) {
      const id = this.getArcId(startNodeId, endNodeId)
      const existingArcs = this.arcs.filter(x => x.id === id)
      return existingArcs
    },
    arcExists (startNodeId, endNodeId) {
      return this.getExistingArcs(startNodeId, endNodeId).length > 0
    },
    setArcSuggestion (startNodeId, endNodeId) {
      this.arcSuggestion = {
        id: this.getArcId(startNodeId, endNodeId),
        startNodeId: startNodeId,
        endNodeId: endNodeId
      }
    },
    addArcFromSuggestion () {
      this.addArc(this.arcSuggestion.startNodeId, this.arcSuggestion.endNodeId)
      this.selectedObject = this.arcs.slice(-1)[0]
      this.arcSuggestion = null
    },
    addArc (startNodeId, endNodeId, capacity = 50) {
      const arc = {
        id: this.getArcId(startNodeId, endNodeId),
        capacity: capacity,
        flow: null,
        startNodeId: startNodeId,
        endNodeId: endNodeId,
        objectType: 'arc'
      }
      this.arcs.push(arc)
    },
    removeArc (id) {
      const existingArc = this.arcs.find(x => x.id === id)
      const index = this.arcs.indexOf(existingArc)
      this.arcs.splice(index, 1)
      if (this.isObjectSelected(id)) {
        this.unselectArc(id)
      }
    },
    selectArc (id) {
      this.selectedObject = this.arcs.find(x => x.id === id)
    },
    unselectArc (id) {
      this.selectedObject = null
    },
    getArcText (arc) {
      if (arc.flow === null) {
        return `${arc.capacity}`
      } else {
        return `${arc.flow} / ${arc.capacity}`
      }
    },
    isObjectSelected (id) {
      if (this.selectedObject === null) {
        return false
      } else if (this.selectedObject.id === id) {
        return true
      } else {
        return false
      }
    },
    runOptimization () {
      this.loading = true
      this.$api.post('/maximum_flows', {
        data: {
          arcs: this.arcs,
          nodes: this.nodes
        }
      }).then(resp => {
        this.results = resp.data.data
        this.addResultsToData()
        this.showResults = true
        this.loading = false
      }).catch(err => {
        this.loading = false
        this.showMessage({
          message: err.response && err.response.data ? err.response.data.message : 'Something went wrong :(',
          color: 'error',
          delay: -1
        })
      })
    },
    addResultsToData () {
      this.arcs.forEach(arc => {
        arc.flow = this.results.arcs.find(x => arc.id === this.getArcId(x.startNodeId, x.endNodeId)).flow
      })
    },
    removeResultsFromData () {
      this.arcs.forEach(arc => {
        arc.flow = null
      })
    },
    removeResults () {
      this.removeResultsFromData()
      this.results = null
      this.showResults = false
    },
    toggleResults () {
      if (this.showResults) {
        this.removeResultsFromData()
        this.showResults = false
      } else {
        this.addResultsToData()
        this.showResults = true
      }
    },
    setNetwork (name = 'small') {
      this.arcs = []
      this.nodes = []
      this.runningId = 0
      this.results = null
      if (name === 'small') {
        this.addNode(50, 150, 'Source', 'Source')
        this.addNode(250, 50, 'Normal')
        this.addNode(250, 150, 'Normal')
        this.addNode(250, 250, 'Normal')
        this.addNode(450, 150, 'Sink', 'Sink')
        this.addArc('Node-1', 'Node-2', 20) // Based on ID
        this.addArc('Node-1', 'Node-3', 30)
        this.addArc('Node-1', 'Node-4', 10)
        this.addArc('Node-2', 'Node-3', 40)
        this.addArc('Node-2', 'Node-5', 30)
        this.addArc('Node-3', 'Node-4', 10)
        this.addArc('Node-3', 'Node-5', 20)
        this.addArc('Node-4', 'Node-3', 5)
        this.addArc('Node-4', 'Node-5', 20)
      } else if (name === 'medium') {
        this.addNode(50, 150, 'Source', 'Source')
        this.addNode(250, 50, 'Normal')
        this.addNode(250, 150, 'Normal')
        this.addNode(250, 250, 'Normal')
        this.addNode(450, 50, 'Normal')
        this.addNode(450, 150, 'Normal')
        this.addNode(450, 250, 'Normal')
        this.addNode(650, 150, 'Sink', 'Sink')
        this.addArc('Node-1', 'Node-2', 20)
        this.addArc('Node-1', 'Node-3', 30)
        this.addArc('Node-1', 'Node-4', 10)
        this.addArc('Node-2', 'Node-3', 40)
        this.addArc('Node-2', 'Node-5', 30)
        this.addArc('Node-3', 'Node-4', 10)
        this.addArc('Node-3', 'Node-5', 20)
        this.addArc('Node-4', 'Node-3', 5)
        this.addArc('Node-4', 'Node-5', 20)
        this.addArc('Node-4', 'Node-6', 25)
        this.addArc('Node-4', 'Node-7', 30)
        this.addArc('Node-5', 'Node-6', 15)
        this.addArc('Node-6', 'Node-8', 10)
        this.addArc('Node-7', 'Node-8', 10)
      } else if (name === 'large') {
        this.addNode(50, 150, 'Source', 'Source')
        this.addNode(250, 50, 'Normal')
        this.addNode(250, 150, 'Normal')
        this.addNode(250, 250, 'Normal')
        this.addNode(450, 50, 'Normal')
        this.addNode(450, 150, 'Normal')
        this.addNode(450, 250, 'Normal')
        this.addNode(250, 350, 'Normal')
        this.addNode(450, 350, 'Normal')
        this.addNode(50, 350, 'Normal')
        this.addNode(650, 150, 'Sink', 'Sink')
        this.addArc('Node-1', 'Node-2', 20)
        this.addArc('Node-1', 'Node-3', 30)
        this.addArc('Node-1', 'Node-4', 10)
        this.addArc('Node-2', 'Node-3', 40)
        this.addArc('Node-2', 'Node-5', 30)
        this.addArc('Node-3', 'Node-4', 10)
        this.addArc('Node-3', 'Node-5', 20)
        this.addArc('Node-4', 'Node-3', 5)
        this.addArc('Node-4', 'Node-5', 20)
        this.addArc('Node-4', 'Node-6', 25)
        this.addArc('Node-4', 'Node-7', 30)
        this.addArc('Node-5', 'Node-6', 15)
        this.addArc('Node-7', 'Node-8', 10)
        this.addArc('Node-1', 'Node-10', 30)
        this.addArc('Node-10', 'Node-7', 25)
        this.addArc('Node-8', 'Node-9', 15)
        this.addArc('Node-9', 'Node-11', 20)
        this.addArc('Node-7', 'Node-11', 35)
        this.addArc('Node-5', 'Node-11', 25)
      }
    },
    ...mapActions(['showMessage'])
  }
}
</script>

<style scoped>
.v-toolbar.v-toolbar--collapsed {
  width: 84px;
}
</style>
