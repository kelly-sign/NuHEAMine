import { predictionEndpoints } from '@/config/predictionEndpoints'

// Centralized metadata for the prediction navigation, routes, page content,
// reserved inputs, and future API integration.
export const predictionModuleConfigs = {
  hardness: {
    key: 'hardness',
    title: 'Hardness Prediction',
    description: 'Predict alloy hardness from elemental composition, processing condition, and phase-structure information.',
    status: 'deployed',
    route: '/prediction/hardness',
    predictionTarget: 'Vickers hardness of high-entropy alloys',
    inputSchema: [
      {
        key: 'composition',
        label: 'Elemental Composition',
        description: 'Atomic percentages of the 15 elements supported by the deployed model',
        type: 'textarea',
        placeholder: 'Enter the alloy elemental composition'
      },
      {
        key: 'processingCondition',
        label: 'Processing Condition',
        description: 'Preparation and heat-treatment condition information',
        type: 'text',
        placeholder: 'Enter the processing condition'
      },
      {
        key: 'phaseStructure',
        label: 'Phase Structure',
        description: 'Available phase or microstructure descriptors',
        type: 'text',
        placeholder: 'Enter the phase structure'
      }
    ],
    outputSchema: [
      {
        key: 'Pred_HV',
        label: 'Predicted Hardness',
        unit: 'HV'
      }
    ],
    apiEndpoint: predictionEndpoints.hardness
  },

  yieldStrength: {
    key: 'yieldStrength',
    title: 'Yield Strength Prediction',
    description: 'Predict alloy yield strength from material composition, processing condition, and microstructure information.',
    status: 'developing',
    route: '/prediction/yield-strength',
    predictionTarget: 'Yield strength of high-entropy alloys',
    inputSchema: [
      {
        key: 'composition',
        label: 'Alloy Composition',
        description: 'Elemental species and their contents',
        type: 'textarea',
        placeholder: 'Reserved for alloy composition input'
      },
      {
        key: 'processingCondition',
        label: 'Processing Condition',
        description: 'Preparation, deformation, and heat-treatment conditions',
        type: 'text',
        placeholder: 'Reserved for processing-condition input'
      },
      {
        key: 'microstructure',
        label: 'Microstructure',
        description: 'Phase, grain-size, and microstructure descriptors',
        type: 'text',
        placeholder: 'Reserved for microstructure input'
      }
    ],
    outputSchema: [
      {
        key: 'yield_strength',
        label: 'Predicted Yield Strength',
        unit: 'MPa'
      }
    ],
    apiEndpoint: predictionEndpoints.yieldStrength
  },

  tensileStrength: {
    key: 'tensileStrength',
    title: 'Tensile Strength Prediction',
    description: 'Predict alloy tensile strength from material composition, processing condition, and microstructure information.',
    status: 'developing',
    route: '/prediction/tensile-strength',
    predictionTarget: 'Ultimate tensile strength of high-entropy alloys',
    inputSchema: [
      {
        key: 'composition',
        label: 'Alloy Composition',
        description: 'Elemental species and their contents',
        type: 'textarea',
        placeholder: 'Reserved for alloy composition input'
      },
      {
        key: 'processingCondition',
        label: 'Processing Condition',
        description: 'Preparation, deformation, and heat-treatment conditions',
        type: 'text',
        placeholder: 'Reserved for processing-condition input'
      },
      {
        key: 'microstructure',
        label: 'Microstructure',
        description: 'Phase, grain-size, and microstructure descriptors',
        type: 'text',
        placeholder: 'Reserved for microstructure input'
      }
    ],
    outputSchema: [
      {
        key: 'tensile_strength',
        label: 'Predicted Tensile Strength',
        unit: 'MPa'
      }
    ],
    apiEndpoint: predictionEndpoints.tensileStrength
  },

  phaseComposition: {
    key: 'phaseComposition',
    title: 'Phase Composition Prediction',
    description: 'Predict the phase composition of an alloy from its elemental composition and processing condition.',
    status: 'developing',
    route: '/prediction/phase-composition',
    predictionTarget: 'Phase constituents and their relative fractions',
    inputSchema: [
      {
        key: 'composition',
        label: 'Alloy Composition',
        description: 'Elemental species and their contents',
        type: 'textarea',
        placeholder: 'Reserved for alloy composition input'
      },
      {
        key: 'processingCondition',
        label: 'Processing Condition',
        description: 'Preparation and heat-treatment condition information',
        type: 'text',
        placeholder: 'Reserved for processing-condition input'
      }
    ],
    outputSchema: [
      {
        key: 'phase_composition',
        label: 'Predicted Phase Composition',
        unit: ''
      }
    ],
    apiEndpoint: predictionEndpoints.phaseComposition
  },

  irradiationHardening: {
    key: 'irradiationHardening',
    title: 'Irradiation Hardening Prediction',
    description: 'Predict irradiation-induced hardening from alloy composition and irradiation conditions.',
    status: 'developing',
    route: '/prediction/irradiation-hardening',
    predictionTarget: 'Irradiation-induced hardness increment',
    inputSchema: [
      {
        key: 'composition',
        label: 'Alloy Composition',
        description: 'Elemental species and their contents',
        type: 'textarea',
        placeholder: 'Reserved for alloy composition input'
      },
      {
        key: 'irradiationDose',
        label: 'Irradiation Dose',
        description: 'Accumulated irradiation damage dose',
        type: 'number',
        min: 0,
        step: 0.1,
        unit: 'dpa',
        placeholder: 'Reserved for irradiation-dose input'
      },
      {
        key: 'irradiationTemperature',
        label: 'Irradiation Temperature',
        description: 'Material temperature during irradiation',
        type: 'number',
        step: 1,
        unit: '°C',
        placeholder: 'Reserved for irradiation-temperature input'
      }
    ],
    outputSchema: [
      {
        key: 'delta_hv',
        label: 'Predicted Hardness Increment',
        unit: 'ΔHV'
      }
    ],
    apiEndpoint: predictionEndpoints.irradiationHardening
  },

  irradiationEmbrittlement: {
    key: 'irradiationEmbrittlement',
    title: 'Irradiation Embrittlement Prediction',
    description: 'Predict irradiation-induced embrittlement from alloy composition and irradiation conditions.',
    status: 'developing',
    route: '/prediction/irradiation-embrittlement',
    predictionTarget: 'Irradiation-induced ductile-to-brittle transition shift',
    inputSchema: [
      {
        key: 'composition',
        label: 'Alloy Composition',
        description: 'Elemental species and their contents',
        type: 'textarea',
        placeholder: 'Reserved for alloy composition input'
      },
      {
        key: 'irradiationDose',
        label: 'Irradiation Dose',
        description: 'Accumulated irradiation damage dose',
        type: 'number',
        min: 0,
        step: 0.1,
        unit: 'dpa',
        placeholder: 'Reserved for irradiation-dose input'
      },
      {
        key: 'irradiationTemperature',
        label: 'Irradiation Temperature',
        description: 'Material temperature during irradiation',
        type: 'number',
        step: 1,
        unit: '°C',
        placeholder: 'Reserved for irradiation-temperature input'
      }
    ],
    outputSchema: [
      {
        key: 'delta_dbtt',
        label: 'Predicted DBTT Shift',
        unit: '°C'
      }
    ],
    apiEndpoint: predictionEndpoints.irradiationEmbrittlement
  }
}

// Home navigation consumes the same module objects used by the router and
// prediction pages, preventing menu labels and route paths from diverging.
export const predictionMenuGroups = [
  {
    key: 'mechanicalProperties',
    title: 'Mechanical Property Prediction',
    icon: '⚙️',
    items: [
      predictionModuleConfigs.hardness,
      predictionModuleConfigs.yieldStrength,
      predictionModuleConfigs.tensileStrength
    ]
  },
  {
    key: 'phaseStructure',
    title: 'Phase Structure Prediction',
    icon: '🧬',
    items: [predictionModuleConfigs.phaseComposition]
  },
  {
    key: 'irradiationPerformance',
    title: 'Irradiation Performance Prediction',
    icon: '☢️',
    items: [
      predictionModuleConfigs.irradiationHardening,
      predictionModuleConfigs.irradiationEmbrittlement
    ]
  }
]
